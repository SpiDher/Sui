/*
/// Module: off_ramp
module off_ramp::off_ramp;
*/

// For Move coding conventions, see
// https://docs.sui.io/concepts/sui-move-concepts/conventions


module off_ramp::OffRamp {
    use sui::event;
    use sui::clock::{Clock, timestamp_ms};
    //use sui::clock;
    

    // One-time witness for initialization
    public struct OFFRAMP has drop {}


    // Struct to store deposit information
    public struct Deposit has key, store {
        id: UID,  // Sui objects must have an `id`
        sender: address,
        amount: u64,
        timestamp: u64,
    }

    // Event to track deposits
    public struct DepositEvent has copy, drop {
        sender: address,
        amount: u64,
        timestamp: u64,
    }

    // Storage for all deposits
    public struct DepositStorage has key, store {
        id: UID,
        deposits: vector<Deposit>,
        admin: address, // Admin for withdrawals
    }

    // Initialize contract with admin address
    fun init(_witness: OFFRAMP, ctx: &mut tx_context::TxContext) {
    let admin = tx_context::sender(ctx); // Set the sender as admin
    let id = object::new(ctx); // Correct object creation

    let storage = DepositStorage {
        id,
        deposits: vector::empty<Deposit>(), // Correct vector usage
        admin,
    };

    transfer::share_object(storage); // Correct function for sharing the object
    }


    // Function to deposit SUI
    public entry fun deposit_sui(storage: &mut DepositStorage, sender: address, clock: &Clock, amount: u64, ctx: &mut tx_context::TxContext) {
        let timestamp = timestamp_ms(clock);
        let deposit = Deposit { id:object::new(ctx), sender, amount, timestamp };
        vector::push_back(&mut storage.deposits, deposit);

        // Emit event for tracking
        event::emit(DepositEvent { sender, amount, timestamp });
    }

    // Admin withdrawal function
    public entry fun withdraw_sui(storage: &mut DepositStorage, admin: address, amount: u64, ctx: &mut tx_context::TxContext) {
        assert!(admin == storage.admin, 1001); // 1001 is an error code for unauthorized access
        
        // Transfer SUI (use a function that actually transfers assets, as transfer_sui() is unbound)
        transfer::public_transfer(amount,tx_context::sender(ctx))
    }
}
