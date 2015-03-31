
#-------------------------------------------------------------------------------

tfFullyCanonicalSig = 0x80000000

#	AccountSet SetFlag/ClearFlag values

asfRequireDest   = 1
asfRequireAuth   = 2
asfDisableMaster = 4

#	account_set

tfRequireDestTag  = 0x00010000
tfOptionalDestTag = 0x00020000
tfRequireAuth     = 0x00040000
tfOptionalAuth    = 0x00080000
tfDisallowSTR     = 0x00100000
tfAllowSTR        = 0x00200000

#	offer_create

tfPassive           = 0x00010000
tfImmediateOrCancel = 0x00020000
tfFillOrKill        = 0x00040000
tfSell              = 0x00080000

#	payment

tfNoRippleDirect = 0x00010000
tfPartialPayment = 0x00020000
tfLimitQuality   = 0x00040000

#	trust_set

tfSetfAuth      = 0x00010000
tfSetNoRipple   = 0x00020000
tfClearNoRipple = 0x00040000
tfClearAuth     = 0x00080000

#-------------------------------------------------------------------------------


def _set_optionals(tx_json, kwargs, optional):
	for key, val in kwargs.iteritems():
		if key in optional:
			tx_json[key] = val


def account_merge(account, destination, sequence, fee):

	tx_json = {
		'TransactionType':	'AccountMerge',
		'Account':			account,
		'Destination':		destination,
		'Flags':			tfFullyCanonicalSig,
		'Sequence':			sequence,
		'Fee':				fee
	}

	return tx_json


def account_set(account, sequence, fee, **kwargs):

	optionals = {
		'InflationDest',	#address
		'SetAuthKey',		#address
		'TransferRate',		#int
		'SetFlag',			#int
		'ClearFlag',		#int
		'Flags',			#int
	}

	tx_json = {
		'TransactionType': 	'AccountSet',
		'Account':			account,
		'Sequence':			sequence,
		'Fee':				fee
	}

	_set_optionals(tx_json, kwargs, optionals)
	tx_json['Flags'] = tx_json.pop('Flags', 0) | tfFullyCanonicalSig

	return tx_json


def offer_cancel(account, offer_sequence, sequence, fee):

	tx_json = {
		'TransactionType':	'OfferCancel',
		'Account':			account,
		'OfferSequence':	offer_sequence,
		'Flags':			tfFullyCanonicalSig,
		'Sequence':			sequence,
		'Fee':				fee
	}

	return tx_json


def offer_create(account, taker_gets, taker_pays, sequence, fee, **kwargs):

	optionals = {
		'OfferSequence',	#int
		'Flags',			#int
	}

	tx_json = {
		'TransactionType':	'OfferCreate',
		'Account':			account,
		'TakerGets':		taker_gets, 			#Amount
		'TakerPays':		taker_pays,				#Amount
		'Sequence':			sequence,
		'Fee':				fee
	}

	_set_optionals(tx_json, kwargs, optionals)
	tx_json['Flags'] = tx_json.pop('Flags', 0) | tfFullyCanonicalSig

	return tx_json


def payment(account, destination, amount, sequence, fee, **kwargs):

	optionals = {
		'DestinationTag',	#int
		'Paths',			#path
		'SendMax',			#amount
		'SourceTag',		#int
		'Flags',			#int
	}

	tx_json = {
		'TransactionType':	'Payment',
		'Account': 			account,
		'Destination': 		destination,
		'Amount': 			amount,
		'Sequence':			sequence,
		'Fee':				fee
	}

	_set_optionals(tx_json, kwargs, optionals)
	tx_json['Flags'] = tx_json.pop('Flags', 0) | tfFullyCanonicalSig

	return tx_json


def set_regular_key(account, regular_key, sequence, fee):

	tx_json = {
		'TransactionType':	'SetRegularKey',
		'Account':			account,
		'Flags':			tfFullyCanonicalSig,
		'Sequence':			sequence,
		'Fee':				fee
	}

	#	If none, remove regular key

	if regular_key:
		tx_json['RegularKey'] = regular_key

	return tx_json


def trust_set(account, amount, sequence, fee, **kwargs):

	optionals = {
		'Flags',			#int
	}

	tx_json = {
		'TransactionType': 	'TrustSet',
		'Account':			account,
		'LimitAmount':		amount,
		'Sequence':			sequence,
		'Fee':				fee
	}

	_set_optionals(tx_json, kwargs, optionals)
	tx_json['Flags'] = tx_json.pop('Flags', 0) | tfFullyCanonicalSig

	return tx_json

#-------------------------------------------------------------------------------
