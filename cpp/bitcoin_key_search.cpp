#include <iostream>
#include <vector>
#include <string>
#include <cstdint>
#include <random>
#include <chrono>
#include <thread>
#include <atomic>
#include <algorithm>
#include <openssl/sha.h>
#include <openssl/evp.h>
#include <secp256k1.h>
#include <gmp.h>

// Wrapper class for mpz_t
class mpz_wrapper
{
public:
    mpz_wrapper() { mpz_init(value); }
    mpz_wrapper(const mpz_wrapper &other) { mpz_init_set(value, other.value); }
    mpz_wrapper &operator=(const mpz_wrapper &other)
    {
        if (this != &other)
        {
            mpz_set(value, other.value);
        }
        return *this;
    }
    ~mpz_wrapper() { mpz_clear(value); }
    mpz_t &get() { return value; }
    const mpz_t &get() const { return value; }

private:
    mpz_t value;
};

// Base58 alphabet
const char *BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";

// Challenge structure
struct Challenge
{
    int id;
    std::string pk_range_start;
    std::string pk_range_end;
    std::string address;
    double prize;
};

// Global variables
std::vector<Challenge> CHALLENGES;

// Function to initialize CHALLENGES
void initializeChallenges()
{
    CHALLENGES.push_back({20, "80000", "fffff", "1HsMJxNiV7TLxmoF6uJNkydxPFDog4NQum", 0.02});
    CHALLENGES.push_back({24, "800000", "ffffff", "1rSnXMr63jdCuegJFuidJqWxUPV7AtUf7", 0.024});
    CHALLENGES.push_back({67, "40000000000000000", "7ffffffffffffffff", "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9", 6.70004315});
}

// Function to convert hexadecimal string to mpz_wrapper
void hex_to_mpz(const std::string &hex, mpz_wrapper &result)
{
    mpz_set_str(result.get(), hex.c_str(), 16);
}

// Function to generate a random mpz_wrapper within a range
void mpz_random_range(mpz_wrapper &result, const mpz_wrapper &range_start, const mpz_wrapper &range_end)
{
    mpz_wrapper range_size;
    mpz_sub(range_size.get(), range_end.get(), range_start.get());
    mpz_add_ui(range_size.get(), range_size.get(), 1);

    gmp_randstate_t state;
    gmp_randinit_default(state);
    gmp_randseed_ui(state, std::random_device{}());

    mpz_urandomm(result.get(), state, range_size.get());
    mpz_add(result.get(), result.get(), range_start.get());

    gmp_randclear(state);
}

// Base58 encoding function
std::string base58_encode(const std::vector<uint8_t> &input)
{
    mpz_wrapper bn;
    mpz_import(bn.get(), input.size(), 1, 1, 0, 0, input.data());

    std::string result;
    mpz_wrapper d;
    mpz_set_ui(d.get(), 58);

    mpz_wrapper r;

    while (mpz_cmp_ui(bn.get(), 0) > 0)
    {
        mpz_fdiv_qr(bn.get(), r.get(), bn.get(), d.get());
        result = BASE58_ALPHABET[mpz_get_ui(r.get())] + result;
    }

    for (size_t i = 0; i < input.size() && input[i] == 0; ++i)
    {
        result = '1' + result;
    }

    return result;
}

// Convert public key to Bitcoin address
std::string pubkey_to_address(const std::vector<uint8_t> &pubkey)
{
    std::vector<uint8_t> sha256(SHA256_DIGEST_LENGTH);
    SHA256(pubkey.data(), pubkey.size(), sha256.data());

    std::vector<uint8_t> ripemd160(EVP_MAX_MD_SIZE);
    unsigned int ripemd160_len;
    EVP_MD_CTX *ctx = EVP_MD_CTX_new();
    EVP_DigestInit_ex(ctx, EVP_ripemd160(), NULL);
    EVP_DigestUpdate(ctx, sha256.data(), SHA256_DIGEST_LENGTH);
    EVP_DigestFinal_ex(ctx, ripemd160.data(), &ripemd160_len);
    EVP_MD_CTX_free(ctx);
    ripemd160.resize(ripemd160_len);

    std::vector<uint8_t> with_version(21);
    with_version[0] = 0x00; // Mainnet version byte
    std::copy(ripemd160.begin(), ripemd160.end(), with_version.begin() + 1);

    std::vector<uint8_t> checksum(SHA256_DIGEST_LENGTH);
    SHA256(with_version.data(), with_version.size(), checksum.data());
    SHA256(checksum.data(), SHA256_DIGEST_LENGTH, checksum.data());

    std::vector<uint8_t> binary_address(25);
    std::copy(with_version.begin(), with_version.end(), binary_address.begin());
    std::copy(checksum.begin(), checksum.begin() + 4, binary_address.begin() + 21);

    return base58_encode(binary_address);
}

// Process a range of private keys
void process_sequential_keys(const mpz_wrapper &start, const mpz_wrapper &end, const std::string &target_address,
                             std::atomic<bool> &found, std::atomic<uint64_t> &total_checked, mpz_wrapper &result)
{
    secp256k1_context *ctx = secp256k1_context_create(SECP256K1_CONTEXT_SIGN);
    std::vector<uint8_t> privkey(32);
    std::vector<uint8_t> pubkey(33);

    mpz_wrapper privkey_mpz, initial_start;
    mpz_random_range(privkey_mpz, start, end);
    initial_start = privkey_mpz;

    while (!found)
    {
        size_t count;
        mpz_export(privkey.data(), &count, 1, 32, 1, 0, privkey_mpz.get());

        secp256k1_pubkey pubkey_struct;
        if (secp256k1_ec_pubkey_create(ctx, &pubkey_struct, privkey.data()))
        {
            size_t pubkey_len = 33;
            secp256k1_ec_pubkey_serialize(ctx, pubkey.data(), &pubkey_len, &pubkey_struct, SECP256K1_EC_COMPRESSED);

            if (pubkey_to_address(pubkey) == target_address)
            {
                found = true;
                result = privkey_mpz;
                break;
            }
        }

        mpz_add_ui(privkey_mpz.get(), privkey_mpz.get(), 1);
        if (mpz_cmp(privkey_mpz.get(), end.get()) > 0)
        {
            privkey_mpz = start;
        }
        if (mpz_cmp(privkey_mpz.get(), initial_start.get()) == 0)
        {
            break;
        }

        total_checked++;
    }

    secp256k1_context_destroy(ctx);
}

int main()
{
    std::cout << "Debug: Program started" << std::endl;

    initializeChallenges();
    std::cout << "Debug: Challenges initialized" << std::endl;

    std::cout << "Select a challenge by its number:" << std::endl;
    for (size_t i = 0; i < CHALLENGES.size(); ++i)
    {
        const Challenge &challenge = CHALLENGES[i];
        std::cout << "#" << challenge.id << ": " << challenge.address
                  << " (Prize: " << challenge.prize << " BTC)" << std::endl;
    }

    int challenge_number;
    std::cout << "\nEnter challenge number: ";
    std::cin >> challenge_number;
    std::cout << "Debug: User entered challenge number: " << challenge_number << std::endl;

    const Challenge *selected_challenge = NULL;
    for (size_t i = 0; i < CHALLENGES.size(); ++i)
    {
        if (CHALLENGES[i].id == challenge_number)
        {
            selected_challenge = &CHALLENGES[i];
            break;
        }
    }

    if (selected_challenge == NULL)
    {
        std::cout << "Invalid challenge number." << std::endl;
        return 1;
    }

    unsigned int num_threads = std::thread::hardware_concurrency();
    std::cout << "Number of cores available: " << num_threads << std::endl;
    std::cout << "Enter the number of threads to use: ";
    std::cin >> num_threads;

    double percentage;
    std::cout << "Enter the percentage of the key range to skip to (e.g., 52.2421): ";
    std::cin >> percentage;

    std::cout << "\nChallenge #" << selected_challenge->id << " Details:" << std::endl;
    std::cout << "Address: " << selected_challenge->address << std::endl;
    std::cout << "Prize: " << selected_challenge->prize << " BTC" << std::endl;
    std::cout << "Private Key Range: " << selected_challenge->pk_range_start
              << "..." << selected_challenge->pk_range_end << std::endl;
    std::cout << "Starting at " << percentage << "% of the key range." << std::endl;

    mpz_wrapper start_range, end_range, total_range, offset;
    hex_to_mpz(selected_challenge->pk_range_start, start_range);
    hex_to_mpz(selected_challenge->pk_range_end, end_range);

    mpz_sub(total_range.get(), end_range.get(), start_range.get());
    mpz_add_ui(total_range.get(), total_range.get(), 1);

    mpz_wrapper percentage_mpz;
    mpz_set_d(percentage_mpz.get(), percentage / 100.0);
    mpz_mul(offset.get(), total_range.get(), percentage_mpz.get());
    mpz_tdiv_q_ui(offset.get(), offset.get(), 100);

    mpz_add(start_range.get(), start_range.get(), offset.get());

    if (mpz_cmp(start_range.get(), end_range.get()) > 0)
    {
        std::cout << "Error: Starting percentage exceeds the key range." << std::endl;
        return 1;
    }

    std::cout << "Using " << num_threads << " threads" << std::endl;

    std::vector<std::thread> threads;
    std::atomic<bool> found(false);
    std::atomic<uint64_t> total_checked(0);
    std::vector<mpz_wrapper> results(num_threads);

    std::chrono::high_resolution_clock::time_point start_time = std::chrono::high_resolution_clock::now();

    mpz_wrapper chunk_size, thread_start, thread_end;
    mpz_sub(chunk_size.get(), end_range.get(), start_range.get());
    mpz_add_ui(chunk_size.get(), chunk_size.get(), 1);
    mpz_tdiv_q_ui(chunk_size.get(), chunk_size.get(), num_threads);

    for (unsigned int i = 0; i < num_threads; ++i)
    {
        mpz_mul_ui(thread_start.get(), chunk_size.get(), i);
        mpz_add(thread_start.get(), thread_start.get(), start_range.get());

        if (i == num_threads - 1)
        {
            thread_end = end_range;
        }
        else
        {
            mpz_add(thread_end.get(), thread_start.get(), chunk_size.get());
            mpz_sub_ui(thread_end.get(), thread_end.get(), 1);
        }

        threads.emplace_back(process_sequential_keys, std::ref(thread_start), std::ref(thread_end),
                             std::ref(selected_challenge->address), std::ref(found),
                             std::ref(total_checked), std::ref(results[i]));
    }

    for (auto &thread : threads)
    {
        thread.join();
    }

    std::chrono::high_resolution_clock::time_point end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double, std::milli> duration = std::chrono::duration_cast<std::chrono::duration<double, std::milli>>(end_time - start_time);

    if (found)
    {
        for (unsigned int i = 0; i < num_threads; ++i)
        {
            if (mpz_cmp_ui(results[i].get(), 0) != 0)
            {
                char *result_str = mpz_get_str(NULL, 16, results[i].get());
                std::cout << "PRIVATE KEY FOUND!: 0x" << result_str << std::endl;
                free(result_str);
                break;
            }
        }
    }
    else
    {
        std::cout << "Private key not found in the given range." << std::endl;
    }

    std::cout << "Total keys checked: " << total_checked << std::endl;
    std::cout << "Total time elapsed: " << duration.count() / 1000.0 << " seconds" << std::endl;
    std::cout << "Overall check rate: " << (total_checked * 1000.0 / duration.count()) << " keys/second" << std::endl;

    return 0;
}