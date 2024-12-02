from .utils import load_json, write_json
from .stack_operator import Stack


def utxo_verify(data):
    valid_tx = []  # 유효성 검사를 통과한 transaction을 저장 후 Mempool에 추가
    transaction_list = []
    response_log = []  # 각 transaction의 처리 결과를 기록하여 반환

    # Transaction ID 생성 및 UTXO 유효성 검사
    # UTXO 파일에서 input UTXO의 존재 여부 검사
    UTXO = load_json("UTXOes.json")  # JSON 파일에서 UTXO 데이터 읽기

    for tx in data:
        try:
            txid, txdata = tx[0], tx[1]
            # Input 데이터 검증
            tx_input = txdata.get("input")
            tx_outputs = txdata.get("outputs")
            tx_script_type = tx_input.get("script type")
            ptxid = tx_input.get("ptxid")
            utxo_amount = tx_input.get("amount") 
            unlocking_script = tx_input.get("unlocking script")
            input_output_index = tx_input.get("output index") 
            unlocking_script_without_redeem_script = ""
            redeem_script = ""

            if tx_script_type == "P2SH":
                unlocking_script_without_redeem_script = tx_input.get(
                    "unlocking script without redeem script"
                )
                redeem_script = tx_input.get("redeem script")
                unlocking_script = unlocking_script_without_redeem_script + ' ' + redeem_script

            # Output 데이터 검증
            total_output_amount = sum(
                int(tx_outputs[output_index]["amount"])  # 계산 시 int로 변환
                for output_index in tx_outputs
            )

            # UTXO와 입력 데이터 비교
            utxo_find = False
            for key in UTXO:
                if key == ptxid:
                    utxo = UTXO[key]
                    for utxo_output_index in utxo:
                        utxo_output_data = utxo[utxo_output_index]
                        utxo_amount_from_utxo = utxo_output_data.get("amount") 
                        locking_script = utxo_output_data.get("locking script")

                        # 일치하는 UTXO 확인
                        if input_output_index == utxo_output_index:  # 문자열로 비교
                            utxo_find = True
                            print("Matching UTXO found")

                            # 금액 검증
                            if int(utxo_amount_from_utxo) != int(utxo_amount):  # 계산 시 int 변환
                                error = "Amount mismatch"
                                log_message = toString_tx_data(
                                    tx, False, error
                                )
                                print(log_message)
                                response_log.append(log_message)
                                break

                            # 스크립트 검증
                            stack = Stack()
                            stack = stack.script_verify(
                                locking_script,
                                unlocking_script,
                                ptxid,
                                unlocking_script_without_redeem_script,
                                redeem_script,
                            )
                            result = stack.CHECKFINALRESULT()
                            print("result : ", result)
                            if not result:
                                error = "Script verification failed"
                                log_message = toString_tx_data(
                                    tx, False, error
                                )
                                response_log.append(log_message)
                            elif tx_script_type == "P2SH" and result:
                                tx[1]["input"] = {
                                    "ptxid" : ptxid,
                                    "output index" : input_output_index,
                                    "amount" : utxo_amount,
                                    "unlocking script" : unlocking_script
                                }
                            break
                if utxo_find:
                    break

            if not utxo_find:
                # UTXO가 존재하지 않을 때 처리
                error = "UTXO not found"
                log_message = toString_tx_data(tx, False, error)
                print(log_message)
                response_log.append(log_message)
                continue

            # 검증을 통과한 transaction 처리
            tx[1]["input"] = {
                "ptxid" : ptxid,
                "output index" : input_output_index,
                "amount" : utxo_amount,
                "unlocking script" : unlocking_script
            }
            log_message = toString_tx_data(tx, True)
            print(log_message)
            response_log.append(log_message)
            valid_tx.append(tx)
            tx[1]["validity"] = True
            transaction_list.append(tx)
        except Exception as e:
            log_message = toString_tx_data(tx, False, str(e))
            response_log.append(log_message)
            tx[1]["input"] = {
                "ptxid" : ptxid,
                "output index" : input_output_index,
                "amount" : utxo_amount,
                "unlocking script" : unlocking_script
                }
            tx[1]["validity"] = False
            transaction_list.append(tx)
            continue

    # Mempool에 검증된 transaction 추가
    mempool = load_json("mempool.json")  # JSON에서 mempool 로드
    for transaction in valid_tx:
        mempool[transaction[0]] = transaction[1]  # txid : tx_data로 저장
    write_json("mempool.json", mempool)  # JSON 파일로 저장
    
    process_log = load_json("process_log.json")
    for transactioin in transaction_list:
        process_log[transaction[0]] = transaction[1]
    write_json("process_log.json", process_log)


# 유효성 검증 결과 출력 형식에 맞춰 문자열 생성
def toString_tx_data(tx, valid, error=""):
    try:
        print(tx)
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
        result.append("")
        return "\n".join(result)
    except Exception as e:
        print(f"Error while generating string for transaction: {e}")
        return f"Error while generating string for transaction: {e}"
    
    