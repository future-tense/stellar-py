stellar-py
==========

Python client library for Stellar

[![PyPI version](https://badge.fury.io/py/stellar-py.svg)](http://badge.fury.io/py/stellar-py)

Still a work in progress, but usable.

# Example usage: sending a payment

```python
import stellar
```

### Generating keys

If you don't have a wallet already, or if you feel a bit paranoid,
this is where you need to start.

```python
account, secret = stellar.generate_keypair()
```

### Connecting to a remote server

```python
remote = stellar.Remote('ws://live.stellar.org:9001')
```

### Sending a payment

```python
amount = stellar.Amount(100) # 100 STR
res = remote.send_payment(secret, account, destination, amount)
```

(NB: Obviously this whole scenario is just fiction, because you can't really do
anything with an account that hasn't been funded.)

# stellar.Remote

Remote is the primary interface in stellar-py, and this is what you'll be using
the most.

```Python
remote = stellar.Remote(url, async=False, callback=None)
```

This creates a `Remote` object, connected to a stellard server located at *url*.

If *async* is True, then all methods that can be asynchronous, by default are so.
This can be overridden in the individual method. If asynchronous, they return an
`aplus` promise for further processing, otherwise they return the actual value.

If a *callback* is provided, network connectivity changes will be communicated
to it.

```Python
def callback(status):
	if status:
		#	connected to network
	else:
		#	disconnected from network
```

### Getting information about accounts

```Python
get_account_currencies(account, ledger_index=None, ledger_hash=None, async=None)
get_account_info(account, async=None)
get_account_lines(account, peer=None, ledger_index=None, ledger_hash=None, async=None)
get_account_offers(account, async=None)
```

### Getting information about order books

```Python
get_book_offers(taker_gets, taker_pays, taker=None, marker=None, ledger_index=None, ledger_hash=None, async=None)
```

### Getting information about ledgers

```Python
get_ledger(full=None, accounts=None, transactions=None, expand=None, ledger_index=None, ledger_hash=None, async=None)
```

### Getting information about transactions

```Python
get_transaction_entry(tx_hash, ledger_index, async=None)
get_tx(transaction, binary=None, async=None)
get_tx_history(start, async=None)
```

### Performing transactions

```Python
cancel_offer(secret, account, offer_sequence, async=None)
create_offer(secret, account, taker_gets, taker_pays, flags=0, async=None, **kwargs)
merge_accounts(secret, account, destination, async=None)
send_payment(secret, account, destination, amount, flags=0, async=None, **kwargs)
set_options(secret, account, flags=0, async=None, **kwargs)
set_regular_key(secret, account, regular_key, async=None)
set_trust(secret, account, amount, flags=0, async=None)
```

### Managing subscriptions

```Python
subscribe(streams=None, accounts=None, accounts_rt=None, books=None, async=None)
unsubscribe(streams=None, accounts=None, accounts_rt=None, books=None, async=None)
add_callback(tx_type, callback)
```

### Getting paths

```Python
get_static_path(source_account, destination_account, destination_amount, async=None)
create_find_path(source_account, destination_account, destination_amount, callback=None, async=None)
close_find_path()
```

### Low-level methods

```Python
get_fee(async=None)
get_sequence_number(account, async=None)
submit_transaction(tx_blob, async=None)
cancel(promise)
```

# stellar.Amount

Amount is a helper class for dealing with amounts and currencies.

100 STR:

```python
amount = stellar.Amount(100)
```

100 USD from *issuer*:

```python
amount = stellar.Amount(100, 'USD', issuer)
```

# Local operations

Everything that can be done locally is done locally. Key pairs are generated
locally, for that extra safety, and the transactions are generated and signed
locally. No secret keys are sent across the network.

The two key operations are
```python
account, secret = stellar.generate_keypair()
tx_blob = stellar.sign(tx_json, secret)
```

## stellar.transactions

This is where we find the functions to generate all of the different transaction
types on the Stellar network. For a description of what the parameters are,
and what they do, check the official documentation over at
https://www.stellar.org/api/#api-submit. Optional parameters are provided
through kwargs. All amounts are in `stellar.Amount`s

```python
tx_json = account_merge(account, destination, sequence, fee)
tx_json = account_set(account, sequence, fee, flags=0, **kwargs)
tx_json = offer_cancel(account, offer_sequence, sequence, fee)
tx_json = offer_create(account, taker_gets, taker_pays, sequence, fee, flags=0, **kwargs)
tx_json = payment(account, destination, amount, sequence, fee, flags=0, **kwargs)
tx_json = set_regular_key(account, regular_key, sequence, fee)
tx_json = trust_set(account, amount, sequence, fee, flags=0)
```
