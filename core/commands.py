from .utils import load_json, write_json
from .utxo_verify import utxo_verify


def push_data(input_callback, output_callback):
    """초기 데이터를 입력하여 UTXO와 STXO를 생성 (GUI와 통합)"""
    transaction_list = []
    while True:
        output_callback("Input data를 입력하세요")
        ptxid = input_callback("Ptxid: ").rstrip()
        output_index = input_callback("Output index: ").rstrip()
        utxo_amount = input_callback("Amount: ").rstrip()
        locking_script = input_callback("Locking script: ").rstrip()
        unlocking_script = input_callback("Unlocking script: ").rstrip()

        # Input 데이터
        input_data = {
            "ptxid": ptxid,
            "output index": output_index,
            "amount": utxo_amount,
            "locking script": locking_script,
            "unlocking script": unlocking_script,
        }

        # Output 데이터
        output_data = {}
        output_idx = 0
        output_callback("Output data")
        while True:
            output_callback(f"Output Index: {output_idx}")
            output_amount = input_callback("Amount: ").rstrip()
            locking_script = input_callback("Locking script: ").rstrip()
            output_data[str(output_idx)] = {
                "amount": output_amount,
                "locking script": locking_script,
            }
            output_idx += 1

            # Output 입력 종료 여부 확인
            while True:
                add_or_done = input_callback("Output 입력을 종료하려면 'done'을, 추가하려면 add를 입력하세요: ").strip().lower()
                if add_or_done == "done" or add_or_done == "add":
                    break
                else:
                    continue
            if add_or_done == "done":
                break
            else:
                continue

        # 트랜잭션 생성 및 txid 계산
        tx_data = {"input": input_data, "outputs": output_data}
        txid = hash_transaction(tx_data)
        tx = [txid, tx_data]
        transaction_list.append(tx)

        # 추가 Input 입력 여부 확인
        while True:
            add_or_done = input_callback("더 많은 Input을 추가하려면 'yes', 종료하려면 'done'을 입력하세요: ").strip().lower()
            if add_or_done == "done" or add_or_done == "add":
                break
            else:
                continue
        if add_or_done == "done":
            break
        else:
            continue

    # STXO와 UTXO에 저장
    STXO = load_json("STXOes.json")
    UTXO = load_json("UTXOes.json")
    for transaction in transaction_list:
        STXO[transaction[0]] = {
            transaction[1]["input"]["output index"]: {
                "amount" : transaction[1]["input"]["amount"],
                "locking script" : transaction[1]["input"]["locking script"]
            }
        }
        UTXO[transaction[0]] = transaction[1]["outputs"]

    write_json("STXOes.json", STXO)
    write_json("UTXOes.json", UTXO)

    # 트랜잭션 결과 반환
    return [to_string_tx_data(tx, True) for tx in transaction_list]

def transaction(input_callback, output_callback):
    """새로운 트랜잭션을 생성 및 검증"""
    transaction_list = []
    while True:
        output_callback("트랜잭션 Input 데이터를 입력하세요.")
        script_type = input_callback("Script type (P2PKH, P2SH, MULTISIG): ").strip().upper()
        ptxid = input_callback("Ptxid: ").strip()
        output_index = input_callback("Utxo output index: ").strip()
        amount = input_callback("Amount: ").strip()
        unlocking_script = ""

        # Unlocking Script 구성
        while True:
            if script_type == "P2PKH":
                sig = input_callback("Sig: ").strip()
                pubkey = input_callback("Pubkey: ").strip()
                unlocking_script = f"{sig} {pubkey}"
            elif script_type == "P2SH":
                unlocking_script_without_redeem_script = input_callback("Unlocking script without redeem script: ").strip()
                redeem_script = input_callback("Redeem script: ").strip()
                unlocking_script = f"{unlocking_script_without_redeem_script} {redeem_script}"
            elif script_type == "MULTISIG":
                sig_list = []
                while True:
                    sig = input_callback("Sig (입력을 완료하려면 'done'): ").strip()
                    if sig.lower() == "done":
                        break
                    sig_list.append(sig)
                unlocking_script = " ".join(sig_list)
            else:
                output_callback(f"Error: 지원되지 않는 script type: {script_type}")
                continue
            break

        # Input 데이터
        input_data = {
            "script type": script_type,
            "ptxid": ptxid,
            "output index": output_index,
            "amount": amount,
            "unlocking script": unlocking_script,
        }
        if script_type == "P2SH":
            input_data["unlocking script without redeem script"] = unlocking_script_without_redeem_script
            input_data["redeem script"] = redeem_script

        # Output 데이터
        output_data = {}
        output_idx = 0
        output_callback("Output data")
        while True:
            output_callback(f"Output Index: {output_idx}")
            output_amount = input_callback("Amount: ").strip()
            locking_script = input_callback("Locking script: ").strip()
            output_data[str(output_idx)] = {
                "amount": output_amount,
                "locking script": locking_script,
            }
            output_idx += 1
            
            # Output 입력 종료 여부 확인
            while True:
                add_or_done = input_callback("Output 입력을 종료하려면 'done'을, 추가하려면 add를 입력하세요: ").strip().lower()
                if add_or_done == "done" or add_or_done == "add":
                    break
                else:
                    continue
            if add_or_done == "done":
                break
            else:
                continue

        # 트랜잭션 생성 및 txid 계산
        tx_data = {"input": input_data, "outputs": output_data}
        txid = hash_transaction(tx_data)
        tx = [txid, tx_data]
        transaction_list.append(tx)

        # Input 추가 여부 확인
        while True:
            add_or_done = input_callback("더 많은 Input을 추가하려면 'yes', 종료하려면 'done'을 입력하세요: ").strip().lower()
            if add_or_done == "done" or add_or_done == "add":
                break
            else:
                continue
        if add_or_done == "done":
            break
        else:
            continue

    # 트랜잭션 검증
    utxo_verify(transaction_list)

    # 트랜잭션 결과 반환
    return [to_string_tx_data(tx, True) for tx in transaction_list]


def mine_block(output_callback):
    
    """mempool의 트랜잭션을 처리하고 UTXO, STXO를 업데이트"""
    mempool = load_json("mempool.json")
    STXO = load_json("STXOes.json")
    UTXO = load_json("UTXOes.json")
    transaction_data = load_json("transaction.json")

    for txid, tx_data in list(mempool.items()):
        output_callback(f"Processing transaction: {txid}")

        # 처리된 트랜잭션 기록
        transaction_data[txid] = tx_data

        # STXO 업데이트 및 UTXO 제거
        tx_input = tx_data["input"]
        ptxid = tx_input["ptxid"]
        input_index = tx_input["output index"]

        if ptxid in UTXO and input_index in UTXO[ptxid]:
            data = UTXO[ptxid][input_index]
            del UTXO[ptxid][input_index]
            if ptxid not in STXO:
                STXO[ptxid] = {}
            STXO[ptxid][str(input_index)] = data
            if not UTXO[ptxid]:
                del UTXO[ptxid]

        # UTXO에 새로운 출력 추가
        for output_index, output_data in tx_data["outputs"].items():
            if txid not in UTXO:
                UTXO[txid] = {}
            UTXO[txid][str(output_index)] = output_data

        # mempool에서 트랜잭션 제거
        del mempool[txid]

    # 업데이트된 데이터 저장
    write_json("mempool.json", mempool)
    write_json("STXOes.json", STXO)
    write_json("UTXOes.json", UTXO)
    write_json("transaction.json", transaction_data)

    output_callback("블록 생성 완료 및 mempool 처리 완료.")
    return "Mining Completed."


def hash_transaction(tx_data):
    """트랜잭션 데이터를 해시화하여 txid 생성"""
    import hashlib
    import pickle

    tx_data_without_unlocking = tx_data.copy()
    tx_data_without_unlocking["input"] = {
        k: v for k, v in tx_data["input"].items() if (k != "unlocking script" and k != "unlocking script without redeem script" and k != "redeem script")
    }
    tx_bytes = pickle.dumps(tx_data_without_unlocking)
    return hashlib.sha256(tx_bytes).hexdigest()


def to_string_tx_data(tx, valid, error=""):
    """트랜잭션 데이터 출력 포맷"""
    try:
        result = [f"Transaction: {tx[0]}"]
        tx_input = tx[1].get("input")
        result.append(
            f"  Input: ptxid = {tx_input.get('ptxid')}, output_index = {tx_input.get('output index')}, "
            f"locking_script = {tx_input.get('locking script')}, unlocking_script = {tx_input.get('unlocking script')}"
        )
        for tx_output_index in tx[1].get("outputs"):
            tx_output_data = tx[1]["outputs"].get(tx_output_index)
            result.append(
                f"  output : {tx_output_index} : amount = {tx_output_data.get('amount')}, locking_script = {tx_output_data.get('locking script')}"
            )
        result.append("  Validity check : " + ("passed" if valid else f"failed at {error}"))

        return result
    except Exception as e:
        return f"Error while generating string for transaction: {e}"


def transaction_with_result(input_callback, output_callback):
    """transaction() 실행 후 결과 반환"""
    return transaction(input_callback, output_callback)


def mine_block_with_result(output_callback):
    """mine_block() 실행 후 결과 반환"""
    return mine_block(output_callback)
