import tkinter as tk
from core.commands import push_data, transaction_with_result, mine_block_with_result


class FullNode:
    def push_data(self, gui_input, gui_output):
        return push_data(gui_input, gui_output)

    def transaction_with_result(self, gui_input, gui_output):
        return transaction_with_result(gui_input, gui_output)

    def mine_block_with_result(self, gui_output):
        return mine_block_with_result(gui_output)


class FullNodeQueryHandler:
    """
    Query.py에서 사용 가능한 쿼리 처리 클래스.
    FullNode의 상태를 조회하고 요청에 응답하는 기능 제공.
    """
    def __init__(self):
        self.transactions_file = "transaction.json"
        self.utxos_file = "UTXOes.json"

    def handle_query(self, query):
        """
        쿼리를 처리하고 결과를 반환
        """
        query = query.strip().lower()
        if query == "snapshot transactions":
            return self.snapshot_transactions()
        elif query == "snapshot utxoset":
            return self.snapshot_utxoset()
        else:
            return {"error": f"Unknown query: {query}"}

    def snapshot_transactions(self):
        """
        현재까지 처리된 트랜잭션 요약 정보를 반환합니다.
        """
        from core.utils import load_json

        try:
            transactions = load_json(self.transactions_file)
            if not transactions:
                return {"transactions": [], "message": "No transactions have been processed yet."}

            results = []
            for txid, tx_data in transactions.items():
                validity = tx_data.get("validity", "unknown")
                results.append(f"Transaction: {txid}, Validity Check: {validity}")
            return results
        except Exception as e:
            return {"error": f"Error retrieving transactions: {str(e)}"}

    def snapshot_utxoset(self):
        """
        현재 시점의 UTXO 집합 상태를 반환합니다.
        """
        from core.utils import load_json

        try:
            utxos = load_json(self.utxos_file)
            if not utxos:
                return {"utxos": [], "message": "No UTXOs available."}

            results = []
            for txid, outputs in utxos.items():
                for index, data in outputs.items():
                    results.append(
                        f"UTXO: txid = {txid}, output_index = {index}, "
                        f"amount = {data.get('amount', 'unknown')}, "
                        f"locking_script = {data.get('locking script', 'unknown')}"
                    )
            return results
        except Exception as e:
            return {"error": f"Error retrieving UTXOs: {str(e)}"}


class FullNodeGUI:
    def __init__(self, root, fullnode):
        self.fullnode = fullnode
        self.root = root
        self.root.title("Blockchain Full Node")
        self.input_field_var = tk.StringVar()  # 사용자 입력 변수
        self.setup_ui()
        self.input_ready = False  # 입력 완료 상태 플래그

    def setup_ui(self):
        """GUI 구성"""
        # 명령어 레이블
        self.command_label = tk.Label(self.root, text="사용할 기능을 선택하세요:", font=("Verdana", 16))
        self.command_label.pack(pady=20)

        # 버튼 구성
        self.push_button = tk.Button(
            self.root, text="Push Data", command=self.execute_push, width=20, height=2
        )
        self.push_button.pack(pady=10)

        self.transaction_button = tk.Button(
            self.root, text="Transaction", command=self.execute_transaction, width=20, height=2
        )
        self.transaction_button.pack(pady=10)

        self.mine_button = tk.Button(
            self.root, text="Mine Block", command=self.execute_mine, width=20, height=2
        )
        self.mine_button.pack(pady=10)

        # 결과 및 입력 영역 (크기 확장)
        self.result_area = tk.Text(self.root, height=30, width=100, wrap=tk.WORD, font=("Verdana", 10))
        self.result_area.pack(pady=10)

        self.input_label = tk.Label(self.root, text="입력:")
        self.input_label.pack()

        self.input_field = tk.Entry(self.root, textvariable=self.input_field_var, width=80)
        self.input_field.pack(pady=10)

        # 엔터키 이벤트 바인딩
        self.input_field.bind("<Return>", self.handle_enter)

    def handle_enter(self, event):
        """엔터키 입력 처리"""
        self.input_ready = True  # 입력이 완료되었음을 알림

    def execute_push(self):
        """Push Data 실행"""
        try:
            result = self.fullnode.push_data(self.gui_input, self.gui_output)
            self.display_result(result, "Push Data 성공")
        except Exception as e:
            self.gui_output(f"Error: {e}")

    def execute_transaction(self):
        """Transaction 실행"""
        try:
            result = self.fullnode.transaction_with_result(self.gui_input, self.gui_output)
            self.display_result(result, "Transaction Broadcast 성공")
        except Exception as e:
            self.gui_output(f"Error: {e}")

    def execute_mine(self):
        """Mine Block 실행"""
        try:
            result = self.fullnode.mine_block_with_result(self.gui_output)
            self.display_result(result, "Mine Block 성공")
        except Exception as e:
            self.gui_output(f"Error: {e}")

    def gui_input(self, prompt):
        """GUI 입력 처리"""
        self.result_area.insert(tk.END, prompt)  # 프롬프트 출력 (줄바꿈 없이)
        self.input_field_var.set("")  # 기존 입력 초기화
        self.input_field.focus()  # 입력 필드에 포커스 설정
        self.input_ready = False  # 입력 상태 초기화

        # 사용자가 입력할 때까지 대기
        while not self.input_ready:
            self.root.update()

        # 입력된 값 가져오기
        user_input = self.input_field_var.get().strip()
        self.result_area.insert(tk.END, f" {user_input}\n")  # 사용자 입력 추가 후 줄바꿈
        self.result_area.see(tk.END)  # 스크롤 처리
        return user_input

    def gui_output(self, message, append_prompt=True, start_new_section=True):
        """GUI 출력 처리"""
        if start_new_section:
            self.result_area.insert(tk.END, "-" * 80 + "\n")  # 구분선 추가

        if append_prompt:
            self.result_area.insert(tk.END, f"{message}\n")
        else:
            # 기존 줄에서 이어쓰기
            self.result_area.insert(tk.END, f"{message}", 'prompt')

        self.result_area.see(tk.END)

    def display_result(self, data, title="결과"):
        """결과를 GUI에 표시"""
        import json

        self.result_area.insert(tk.END, "-" * 80 + "\n")  # 출력 단위 구분선 추가
        self.result_area.insert(tk.END, f"==== {title} ====\n\n")

        formatted_result = json.dumps(data, indent=4, ensure_ascii=False)
        self.result_area.insert(tk.END, formatted_result + "\n")

        self.result_area.insert(tk.END, "\n" + "-" * 80 + "\n")  # 출력 끝 구분선 추가
        self.result_area.see(tk.END)



if __name__ == "__main__":
    root = tk.Tk()
    app = FullNodeGUI(root, FullNode())
    root.mainloop()
