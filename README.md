FORMAT: 1A

# Addressimo

*Addressimo* is an open source, digital currency address service written in Python.

<img src="http://i.imgur.com/xVbvrZz.png" width="300">

### Download

*Addressimo* is available for download here:
 
[**https://github.com/netkicorp/addressimo**](https://github.com/netkicorp/addressimo)

# Overview

*Addressimo* is an address service. While there are many ways to generate and/or receive an address, the end result always involves
the requesting entity recvieving an address to which they can send value.  The value of a service such as *Addressimo* is that
 it helps to provide additional security and privacy surrounding address generation / requests.
 
Quite simply, a wallet can receive different address types just by making an address request like this:

**https://addressimo_site_url/address/{id}/resolve**
 
## Supported Functionality
 
### Address Generation

* [Static Wallet Addresses](#static-anchor)
* [BIP0032-based HD-Wallet Addresses](#bip32-anchor)

### Address Retrieval

* [BIP0021 / BIP0072 URI](#bituri-anchor)
* [BIP0070 PaymentRequest](#pr-anchor)
* [InvoiceRequests (Encrypted PaymentRequests)](#ir-anchor) 

### PaymentRequest Pathways

* [Full PaymentRequest, Payment, and PaymentACK Processing Support](#fullflow-anchor)
* [PaymentRequest Store & Forward](#sf-anchor)
* [InvoiceRequests (Encrypted PaymentRequests)](#ir-anchor) 

<a name="static-anchor"/>
A **Static Address** is a single, non-changing address. Due to the potential for privacy leaks, it is generally not considered best practice to use static addresses,
 but some wallets may only support a single, static address.

<a name="bip32-anchor"/>
**BIP0032** address generation is based on an extended master public key as well as a Redis-stored blockchain used *address
cache* that is maintained via a cronjob. If an address has been used in a transaction output on the blockchain, the next
index will be tried for *[BIP0032](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)* wallet address generation.

<a name="pr-anchor"/>
**BIP0070 PaymentRequest** generation can use wallet addresses based on a *static wallet address* or a 
*[BIP0032](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki)* wallet address that is generated based 
on the logic previously explained. *[BIP0070 PaymentRequests](https://github.com/bitcoin/bips/blob/master/bip-0070.mediawiki)* are 
created and signed on demand using the endpoint's configured private key (or configured signer plugin) and x509 cert.

<a name="bituri-anchor"/>
The **Bitcoin URI** is defined in [BIP0021](https://github.com/bitcoin/bips/blob/master/bip-0021.mediawiki), with extensions
 defined in [BIP0072](https://github.com/bitcoin/bips/blob/master/bip-0072.mediawiki) in order to support 
 [BIP0070](https://github.com/bitcoin/bips/blob/master/bip-0070.mediawiki) PaymentRequests and later PaymentRequest extensions. 
 The Bitcoin URI was created *"to enable users to easily make payments by simply clicking links on webpages or scanning QR Codes".*
 
| BIP     | Example Bitcoin URI  |
| --- | --- |
| BIP0021 | bitcoin:175tWpb8K1S7NmH4Zx6rewF9WQrcZv245W?amount=50&label=Luke-Jr&message=Donation%20for%20project%20xyz |
| BIP0072 | bitcoin:mq7se9wy2egettFxPbmn99cK8v5AFq55Lx?amount=0.11&r=https://merchant.com/pay.php?h%3D2a8628fc2fbe    |  
 

## Address Resolution
*Addressimo* provides address resolution services based on the configuration of the *Addressimo* endpoint. Depending on that 
configuration, the resolution endpoint can return:

1. [BIP0072](https://github.com/bitcoin/bips/blob/master/bip-0072.mediawiki) [Bitcoin URI](#bituri-anchor) in plaintext
2. A PaymentRequest if the URL's bip70 query parameter is set to true

<a name="fullflow-anchor"/>
## Full PaymentRequest, Payment, and PaymentACK Processing
*Addressimo* implements end-to-end [BIP0070](https://github.com/bitcoin/bips/blob/master/bip-0070.mediawiki) PaymentRequest, 
Payment, PaymentACK handling. PaymentRequests are generated via the various methods described in this document. If an 
endpoint is not configured with a payment_url, *Addressimo* will generate a unique payment_url when generating a PaymentRequest 
and assume responsibility for Payment and PaymentACK handling.

Upon receiving a Payment message, *Addressimo* will validate the Payment message according to the specification defined 
for [BIP0070](https://github.com/bitcoin/bips/blob/master/bip-0070.mediawiki). If a Payment message is deemed valid and 
satisfies all requirements of the generated PaymentRequest, *Addressimo* will submit the Payment to the P2P network and 
respond with a PaymentACK.

**NOTE:** *Addressimo* can only handle Payments for PaymentRequests that are generated by *Addressimo*. *Addressimo* 
does not have the necessary information to handle Payment validation for [Store & Forward](#sf-anchor) or encrypted PaymentRequests.

<a name="sf-anchor"/>
## Store & Forward

Additionally, *Addressimo* can act as a **Store & Forward** server for **pre-signed** PaymentRequests. This is particularly useful for purely
mobile wallets that would otherwise need to be online in order to create and sign *PaymentRequests*. The *Store & Forward* functionality is as follows:

* Register an endpoint
* Add Stored PaymentRequests
* Get Available PaymentRequest Count
* Delete Endpoint

The **Store & Forward PaymentRequests** are available in the same way as the create and sign on demand *PaymentRequests*, 
and are retrieved in the general *Addressimo* address lookup request (described in the top of this document and documented below).

<a name="ir-anchor"/>
## InvoiceRequests (Encrypted PaymentRequests)

### Acronyms

| Acronym   | Expanded                  | Description                                               |
| --------- | ------------------------- | --------------------------------------------------------- |
| IR        | InvoiceRequest            | A request to return a ReturnPaymentRequest                |
| RPR       | ReturnPaymentRequest      | A PaymentRequest returned based on an InvoiceRequest      |

### Functionality
InvoiceRequests (IR) and ReturnPaymentRequests (RPR) comprise a set of functionality that allows parties to submit an InvoiceRequest
and return at a later time to retrieve a ReturnPaymentRequest. This allows for two parties to exchange 
an encrypted PaymentRequest without exposing the PaymentRequest details to 3rd parties **or** an address service such as *Addressimo*. 
This functionality is enabled when the ir_only configuration flag is enabled for an endpoint.

#### Newly Introduced Message Types

##### InvoiceRequest Message

| Field | Type | Description |
|:---|:---|:---|
| sender_public_key     | bytes     | Sender's EC Public Key |
| nonce                 | uint64    | Microseconds since epoch, always increasing |
| amount                | uint64    | amount is integer-number-of-satoshis (default: 0) |
| pki_type              | string    | none / x509+sha256 (default: "none") |
| pki_data              | bytes     | Depends on pki_type |
| notification_url      | string    | URL to notify on ReturnPaymentRequest ready |
| signature             | bytes     | PKI-dependent signature |

The InvoiceRequest message definition requires only the sender_public_key and nonce. *Addressimo* will validate the **sender_public_key** 
matches the public key in the X-Identity header.

**Nonce** must be ever-increasing. *Addressimo* enforces that the initial **Nonce** value between 2 entities is no less than 
X seconds less than current UTC time (where X is configurable). Also, *Addressimo* enforces the ever-increasing nature of a nonce 
between two entities. 

When **pki_type** == "x509_sha256", **pki_data** must contain serialized a **X509Certificates** message which matches PaymentRequest
specifications. Similarly, the message **signature** must be present and contain the message signature (using the X509 private key)
where **signature** is an empty string.

##### ReturnPaymentRequest Message

| Field | Type | Description |
|:---|:---|:---|
| encrypted_payment_request | bytes | AES-256-CBC Encrypted PaymentRequest as defined in this spec |
| receiver_public_key       | bytes | Receiver's EC Public Key (SECP256K1) |
| payment_request_hash      | bytes | SHA256 Hash of Non-Encrypted, Serialized PaymentRequest (used for validation) |

**NOTE**: Check addressimo/paymentrequest/paymentrequest.proto Protobuf definition file for complete message definition.

### Process

The process that defines this interaction that is supported in *Addressimo* is described here:

**NOTE:** The sender is the entity wishing to send value to the receiver.

1. Sender submits an InvoiceRequest **(New Message Type)** to an *Addressimo* endpoint configured for InvoiceRequests.
2. Sender receives a 202 Accepted response from *Addressimo* with a Location header that will eventually return a newly returned ReturnPaymentRequest (RPR)
3. Receiver polls *Addressimo* for queued InvoiceRequests
4. Receiver receives queued InvoiceRequests from *Addressimo*
5. Receiver creates the PaymentRequest to be returned to the sender
6. Receiver generates SHA256 hash of the serialized PaymentRequest
7. Receiver generates a secret exponent for later use in PaymentRequest encryption using [ECDH](https://en.wikipedia.org/wiki/Elliptic_curve_Diffie–Hellman). *NOTE: The secret exponent is the X component of the identified ECDH-derived point.*
8. Receiver generates encryption key and initialization vector using [HMAC_DRBG](http://csrc.nist.gov/publications/nistpubs/800-90A/SP800-90A.pdf) also referenced in [RFC6979](https://tools.ietf.org/html/rfc6979) in the following way:
    * HMAC_DRBG Initialization Entropy is set to the string value of the secret exponent generated in Step 7
    * HMAC_DRBG Initialization Nonce is set to the string value of the InvoiceRequest's nonce (*received in Step 4*)
    * Encryption Key = HMAC_DRBG.GENERATE(32) - 256 bits
    * IV = HMAC_DRBG.GENERATE(16) - 128 bits
9. Receiver encrypts the PaymentRequest using AES-256-CBC using the generated Encryption Key and IV.
10. Receiver creates a ReturnPaymentRequest **(New Message Type)** and sets all required fields
11. Receiver submits the encrypted ReturnPaymentRequest to *Addressimo*
11. Sender polls *Addressimo* URL returned in Step 2 for ReturnPaymentRequest retrieval
12. Sender receives and parses the *ReturnPaymentRequest* object
13. Sender determines ECDH ephemeral key using the flow described in Step 7
14. Sender decrypts **encrypted_payment_request** using AES-256-CBC and the parameters described in Step 8
15. Sender validates **payment_request_hash** by SHA256 hashing the decrypted, serialized PaymentRequest
16. Sender de-serializes and uses the decrypted PaymentRequest

An example of this flow can be seen in **functest/functest_ir.py**

### Systemic Improvements

1. **Prevent Key Leakage:** Since the receiver has to approve and create a PaymentRequest they are only giving a payment address to the sender *if* they approve the PaymentRequest.
2. **Prevent PaymentRequests Interception:** The received creates the PaymentRequest and encrypts it such that only the sender can decrypt to PaymentRequest in order to use it.

# Setup

## Requirements
1. Python 2.7.9+
2. RPC access to a running full-node bitcoin server.
3. A running Redis service 

**DB SELECTION NOTE:** Redis is used by default, but you can use any datastore you can write resolver code for. To do this, make sure to 
inherit from BaseResolver and create a PR once complete!

**MEMORY USE NOTE:** A full bitcoin address cache can take 2G+ of space on disk / memory. Please make sure you have enough resources to run the service.


## Installation

##### In order to run *Addressimo* (managed by supervisor), please follow these steps:

    git clone https://github.com/netkicorp/addressimo.git
    pip install supervisor
    mkdir -p /var/log/addressimo
    chown appuser:appuser /var/log/addressimo
    
##### Add this supervisor configuration stanza to */etc/supervisord.conf* after making any changes:
    
    [program:addressimo]
    command = /path/to/bin/python /path/to/bin/gunicorn server:app -b0.0.0.0:5000 -w 4 --timeout 60 --log-level debug --access-logfile /var/log/addressimo/addressimo_access.log --log-file /var/log/addressimo/addressimo.log
    directory = /home/appuser/addressimo
    user = appuser
    numprocs=1
    stdout_logfile=/var/log/addressimo/addressimo.log
    stderr_logfile=/var/log/addressimo/addressimo_err.log
    autostart=true
    autorestart=true
    startsecs=10
    priority=800
    environment= PYTHONPATH="$PYTHONPATH:/use/only/for/virtualenvs"
    
##### Update Addressimo configuration parameters in $ADDRESSIMO_HOME/addressimo/config.py

The configuration parameters are named in order to be understandable. The main things to be concerned with here
are bitcoin service config and redis service config. There are various other parameters that provide defaults for *Addressimo*.
    
##### Add Build Address Cache cronjob:

    PYTHONPATH=/use/only/for/virtualenvs

    * * * * * /path/to/bin/python /home/appuser/addressimo/jobs/build_address_cache.py >> /var/log/addressimo/build_address_cache.log 2>&1
    
**NOTE:** Upon first run, build_address_cache.py will run through the entire blockchain to load the address cache. This **will** 
take some time! In order for *Addressimo* to start resolving endpoints, you will need to wait until the initial load is complete to start-up the service.

##### Start Addressimo:
    
    supervisor start addressimo    

# Group Addressimo

<a name="auth-anchor"/>
### Endpoint Authentication and Request Validation

Authentication and verification for some endpoints is based on [BitPay's](https://bitpay.com/api) signed request process.
If you're interested in reading through Bitpay's API documentation regarding the X-Identity and X-Signature headers, it 
can be found [here](https://bitpay.com/api#making-requests).

All requests require both the X-Identity and X-Signature headers to be present and valid. The X-Identity header is the hex-encoded
ECDSA public key for the private key that was used to sign the request. The X-Signature header is the hex-encoded ECDSA signature
of the message that is computed as follows:

privkey.sign( **url** + **request data content** )

For example, when submitting the following request data to https://addressimo.netki.com/address/longUuid/resolve:

{"key":"value"}

The API request would have a signature that has signed the string: https://addressimo.netki.com/address/longUuid/resolve{"key":"value"}

**NOTE:** An endpoint that requires this method of authentication and verification is denoted with **[REQUIRES AUTHENTICATION](#auth-anchor)**

## Address Resolution [/address/{id}/resolve]

### Immediate Address Resolution [GET]

**NOTE:** The address lookup can return a simple wallet address via the defined JSON format below **OR** it can return a BIP0070 PaymentRequest.
The response type can be determined by looking at the Content-Type in the API response.

+ Parameters

    - id (required, string, `f282ad27e92f4e518a0738dd99469470`) ... Address Resolution ID

+ Response 200 (application/json)

        {
            "success": true,
            "message": "",
            "wallet_address": "1CpLXM15vjULK3ZPGUTDMUcGATGR9xGitv"
        }
        
+ Response 200 (application/bitcoin-paymentrequest)

        SERIALIZED BINARY PROTOBUF PaymentRequest
        
+ Response 400 (application/json)

        {
            "success": false,
            "message": "misconfiguration or bad request message"
        }
        
+ Response 404 (application/json)

        {
            "success": false,
            "message": "not found message"
        }
        
+ Response 405 (application/json)

    **NOTE:** This resolve endpoint requires that an [InvoiceRequest](#ir-anchor)  be created.

    + Headers
    
            Allow: "POST"
            
    + Body
    
            {
                "success": false,
                "message": "Endpoint Requires a valid POST to create a PasymentRequest Request"
            }
        
+ Response 500 (application/json)

        {
            "success": false,
            "message": error_message
        }
        
### InvoiceRequest Submission [POST]

**[REQUIRES AUTHENTICATION](#auth-anchor)**

In addition to the existing authentication requirement, if an x509 certificate is used in the InvoiceRequest, the request must be 
signed by the x509 certificate's private key. In this case, the process of signing the request would happen two times as defined here:

1. Create InvoiceRequest with the signature field set to ""
2. Sign the InvoiceRequest using the X509 Certificate's Private Key
3. Set the InvoiceRequest's signature field to the signature from Step 2.
4. Sign URL + Serialized InvoiceRequest with the ECDSA Private Key (as described above)

**NOTE:** The Location header returned from the POST call is used to retrieve the pending ReturnPaymentRequest.

+ Parameters

    - id (required, string, `f282ad27e92f4e518a0738dd99469470`) ... Address Resolution ID

+ Request (application/bitcoin-invoicerequest)

    + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"
            Content-Transfer-Encoding: "binary"
            
    + Body

            Serialized InvoiceRequest
        
+ Response 202

    + Headers
        
            Location: "https://site_url/returnpaymentrequest/longUuid"
    
+ Response 400 (application/json)

        {
            "success": false,
            "message": "Requests including x509 cert must include signature"
        }

+ Response 404 (application/json)

        {
            "success": false,
            "message": "ID Not Recognized"
        }
            

## Store & Forward [/address/{id}/sf]
        
**[REQUIRES AUTHENTICATION](#auth-anchor)**

### Create Store & Forward Endpoint [POST /sf]

The "id" returned in the POST call will need to be used for any further access to the Store & Forward functionality.
   
+ Request (application/json)

    + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"

+ Response 200 (application/json)

        {
            "success": true,
            "message": "",
            "id': "newly_created_endpoint_id",
            "endpoint": "https://site_url/address/newly_created_endpoint_id/resolve"
        }
        
+ Response 500 (application/json)

        {
            "success": false,
            "message": "error_message"
        }

### Add Presigned PaymentRequests to Store & Forward Endpoint [PUT]

+ Parameters

    + id (required, string, `f282ad27e92f4e518a0738dd99469470`) ... Store & Forward Endpoint ID
   
+ Request (application/json)

    + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"
            
    + Body

            {
                "presigned_payment_requests": [
                    "HEX ENCODED PRESIGNED & SERIALIZED PaymentRequest #1",
                    "HEX ENCODED PRESIGNED & SERIALIZED PaymentRequest #2",
                    "HEX ENCODED PRESIGNED & SERIALIZED PaymentRequest #N"
                ]
            }

+ Response 200 (application/json)

        {
            "success": true,
            "message": "",
            "payment_requests_added": 5
        }
        
+ Response 400 (application/json)

        {
            "success": false,
            "message": "bad request error message"
        }
        
+ Response 404 (application/json)

        {
            "success": false,
            "message": "Invalid Identifier"
        }
        
### Delete Store & Forward Endpoint [DELETE]

+ Parameters

    + id (required, string, `f282ad27e92f4e518a0738dd99469470`) ... Store & Forward Endpoint ID
   
+ Request (application/json)

    + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"
            
+ Response 204 (application/json)


+ Response 404 (application/json)

        {
            "success": false,
            "message": "Invalid Identifier"
        }
        
### Get Presigned PaymentRequest Count [GET]

+ Parameters

    + id (required, string, `f282ad27e92f4e518a0738dd99469470`) ... Store & Forward Endpoint ID
   
+ Request (application/json)

    + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"

+ Response 200 (application/json)

        {
            "success": true,
            "message": "",
            "payment_request_count": 5
        }
        
+ Response 404 (application/json)

        {
            "success": false,
            "message": "Invalid Identifier"
        }

## InvoiceRequests [/address/{id}/invoicerequests]

**[REQUIRES AUTHENTICATION](#auth-anchor)**

### Retrieve InvoiceRequests [GET]

Retrieve queued InvoiceRequests for the given endpoint.
   
+ Request (application/json)

    + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"

+ Response 200 (application/json)

        {
            "success": true,
            "message": "",
            "count": 1,
            "requests": [
                {
                    "id": "longUuid",
                    "invoice_request": HEX ENCODED, SERIALIZED InvoiceRequest
                    "submit_date": 1439944603
                }
            ]
        }
        
+ Response 404 (application/json)

        {
            "success": false,
            "message": "Invalid Identifier"
        }
        
+ Response 500 (application/json)

        {
            "success": false,
            "message": "Unable to Retrieve Queued PR Requests"
        }

### Submit ReturnPaymentRequest [POST]

Submit ReturnPaymentRequest messages to be held until they are retrieved.

+ Request (application/json)

    + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"
            
    + Body

            {
                "ready_requests": [
                    {
                        "id": "longUuid",
                        "return_payment_request": "HEX ENCODED, SERIALIZED ReturnPaymentRequest"
                    }
                ]
            }


+ Response 200 (application/json)

        {
            "success": true,
            "message": "",
            "accept_count": 1
        }
        
+ Response 400 (application/json)

        {
            "success": "false",
            "message": "Submitted Return PaymentRequests contain errors, please see failures field for more information",
            "accept_count": 0
            "failures": {
                "longUuid": "Missing Required Fields"
            }
        }
        
+ Response 400 (application/json)

        {
            "success": "false",
            "message", "Invalid Request"
        }
        
+ Response 404 (application/json)

        {
            "success": "false",
            "message", "Invalid Identifier"
        }
        
+ Response 500 (application/json)

        {
            "success": false,
            "message": "error_message"
        }

### ReturnPaymentRequest Retrieval [GET /returnpaymentrequest/{id}]

Retrieve a ReturnPaymentRequest message by ID.

**NOTE:** This message contains an encrypted PaymentRequest that can only decrypted by the original requestor.

+ Parameters

    - id (required, string, `f282ad27e92f4e518a0738dd99469fdsfasdgfdgt34t4hh45ujy470`) ... RPR ID
    
+ Response 200 (application/bitcoin-returnpaymentrequest)

    + Headers
    
            Content-Transfer-Encoding: binary
    
    + Body
        
            BINARY, SERIALIZED ReturnPaymentRequest
        
+ Response 404 (application/json)

        {
            "success": false,
            "message": "PaymentRequest Not Found or Not Yet Ready"
        }
        
+ Response 500 (application/json)

        {
            "success": false,
            "message": "PaymentRequest Not Found"
        }
        
## Payment Handling [/payment]
### Submit Payment Message [POST /payment/{id}]

+ Parameters

   + id (required, string, `f282ad27e92f4e518a0738dd99469fdsfasdgfdgt34t4hh45ujy470`) ... Payment URL ID

+ Request (application/bitcoin-payment)

   + Headers

            Accept: "application/bitcoin-paymentack"
            Content-Transfer-Encoding: "binary"
           
   + Body

            BINARY, SERIALIZED PROTOBUF PAYMENT
   
+ Response 200 (application/bitcoin-paymentack)

            BINARY, SERIALIZED PROTOBUF PAYMENTACK
       
+ Response 400 (application/json)

        {
           "success": false,
           "message": "Invalid Payment Submitted"
        }
       
+ Response 404 (application/json)

        {
           "success": false,
           "message": "Unable to Retrieve PaymentRequest associated with Payment."
        }
       
+ Response 500 (application/json)

        {
           "success": false,
           "message": "Error Retrieving PaymentRequest."
        }        

### Retrieve Refund Outputs [GET /payment/{id}/refund/{tx}]

+ Parameters

   + id (required, string, `f282ad27e92f4e518a0738dd99469fdsfasdgfdgt34t4hh45ujy470`) ... Address Resolution ID
   + tx (required, string, `d69cb176808acb4cee2a31fac98b29550ad82dcc21b144dc5704c891bc22ded4`) ... TX HASH

+ Request (application/bitcoin-payment)

   + Headers

            X-Identity: "HEX ENCODED ECDSA PUBLIC KEY"
            X-Signature: "HEX ENCODED ECDSA MESSAGE SIGNATURE"
   
+ Response 200 (application/bitcoin-paymentack)

        {
           "success": true,
           "message": "",
           "memo": "Payment memo",
           "refund_to": "['76a914819d3b204b99f252da2ef21293c621e75dd1444f88ac']"
        }
       
+ Response 404 (application/json)

        {
           "success": false,
           "message": "Refund Output Not Found For Submitted TX."
        }
        
# Utility Functionality
## Get Server Time [GET /time]
+ Request (application/json)

+ Response 200 (application/json)

        {
            "success": true,
            "message": "",
            "utime": 1452797108831686
        }