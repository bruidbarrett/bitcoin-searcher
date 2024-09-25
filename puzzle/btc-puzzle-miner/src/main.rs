use sha2::Digest;
use std::sync::mpsc::{channel, Sender, Receiver};
use std::sync::Arc;
use std::time::{Instant, Duration};
use std::collections::HashMap;
use std::thread;
use std::io::{self, Write};

fn decode_address_to_pubhash(address: &str) -> [u8; 20] {
    let decoded = bs58::decode(address).into_vec().unwrap();
    let mut pubhash = [0u8; 20];
    pubhash.copy_from_slice(&decoded[1..21]);
    pubhash
}

struct HashUpdate {
    thread_id: usize,
    hash_count: u64,
}

fn mine(pubhash: [u8; 20], start_private_key: [u8; 32], thread_id: usize, log_sender: Sender<HashUpdate>) -> Option<[u8; 32]> {
    let secp = secp256k1::Secp256k1::new();
    let mut sha_hasher = sha2::Sha256::new();
    let mut ripemd_hasher = ripemd::Ripemd160::new();
    let mut mined_private_key = start_private_key;
    let mut local_hash_count = 0u64;
    const REPORT_INTERVAL: u64 = 10_000;
    
    loop {
        let secret_key = secp256k1::SecretKey::from_slice(&mined_private_key).unwrap();
        let public_key = secp256k1::PublicKey::from_secret_key(&secp, &secret_key);
        let compressed_pubkey = public_key.serialize();
        sha_hasher.update(&compressed_pubkey);
        let public_key_sha_hash = sha_hasher.finalize_reset();
        ripemd_hasher.update(&public_key_sha_hash);
        let p2pkh_pubkey_hash = ripemd_hasher.finalize_reset();
        
        if p2pkh_pubkey_hash == pubhash.into() {
            return Some(mined_private_key);
        }
        
        let mut i = mined_private_key.len() - 1;
        loop {
            mined_private_key[i] = mined_private_key[i].wrapping_add(1);
            if mined_private_key[i] != 0 {
                break;
            }
            if i == 0 {
                break;
            }
            i -= 1;
        }
        
        local_hash_count += 1;
        if local_hash_count % REPORT_INTERVAL == 0 {
            log_sender.send(HashUpdate { thread_id, hash_count: REPORT_INTERVAL }).unwrap();
        }
    }
}

fn logging_thread(log_receiver: Receiver<HashUpdate>) {
    let mut last_log_time = Instant::now();
    let mut thread_hashes = HashMap::new();
    let log_interval = Duration::from_secs(1);

    loop {
        while let Ok(update) = log_receiver.try_recv() {
            *thread_hashes.entry(update.thread_id).or_insert(0) += update.hash_count;
        }

        let now = Instant::now();
        if now.duration_since(last_log_time) >= log_interval {
            let elapsed = now.duration_since(last_log_time).as_secs_f64();
            let total_hashes: u64 = thread_hashes.values().sum();
            let hashes_per_second = total_hashes as f64 / elapsed;

            println!("Aggregate hashes per second: {:.2}", hashes_per_second);
            for (thread_id, hashes) in &thread_hashes {
                println!("  Thread {}: {:.2} H/s", thread_id, *hashes as f64 / elapsed);
            }

            thread_hashes.clear();
            last_log_time = now;
        }

        thread::sleep(Duration::from_millis(100));
    }
}

fn parallel_mine(pubhash: [u8; 20], thread_count: usize) -> Option<[u8; 32]> {
    use rayon::prelude::*;

    rayon::ThreadPoolBuilder::new()
        .num_threads(thread_count)
        .build_global()
        .unwrap();

    let (log_sender, log_receiver) = channel();

    let log_thread = thread::spawn(move || {
        logging_thread(log_receiver);
    });

    let result = (0..thread_count)
        .into_par_iter()
        .find_map_any(|i| {
            let mut start_private_key = [1u8; 32];
            start_private_key[0] = i as u8;
            let thread_log_sender = log_sender.clone();
            
            mine(pubhash, start_private_key, i, thread_log_sender)
        });

    // If a result is found, we should terminate the log thread
    // In a real application, you'd want to implement a proper shutdown mechanism
    if result.is_some() {
        // This is a simple way to stop the logging thread, but it's not graceful
        // In a real application, you'd want to send a specific shutdown message
        drop(log_sender);
        log_thread.join().unwrap();
    }

    result
}

fn main() {
    println!("Enter the number of threads to use:");
    io::stdout().flush().unwrap();
    let mut threads = String::new();
    io::stdin().read_line(&mut threads).unwrap();
    let thread_count: usize = threads.trim().parse().unwrap();

    let address = "1BY8GQbnueYofwSuFAT3USAhGjPrkxDdW9";
    let pubhash = decode_address_to_pubhash(address);
    
    if let Some(private_key) = parallel_mine(pubhash, thread_count) {
        println!("Found private key: {:?}", hex::encode(private_key));
    } else {
        println!("Mining terminated without finding a solution.");
    }
}
