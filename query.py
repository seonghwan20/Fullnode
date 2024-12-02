import tkinter as tk
from fullnode import FullNodeQueryHandler

class QueryGUI:
    def __init__(self, root):
        self.handler = FullNodeQueryHandler()  # 쿼리 핸들러 초기화
        self.root = root
        self.root.title("Blockchain Query Interface")
        self.setup_ui()

    def setup_ui(self):
        """GUI 구성"""
        # 명령어 버튼
        self.snapshot_tx_button = tk.Button(
            self.root, text="Snapshot Transactions", command=self.query_transactions, width=30, height=2
        )
        self.snapshot_tx_button.pack(pady=10)

        self.snapshot_utxo_button = tk.Button(
            self.root, text="Snapshot UTXO Set", command=self.query_utxoset, width=30, height=2
        )
        self.snapshot_utxo_button.pack(pady=10)

        # 결과 출력 영역
        self.result_area = tk.Text(self.root, height=30, width=100, wrap=tk.WORD, font=("Verdana", 10))
        self.result_area.pack(pady=10)
        self.result_area.config(state=tk.DISABLED)  # 읽기 전용 설정

    def query_transactions(self):
        """Snapshot Transactions 명령 실행"""
        result = self.handler.handle_query("snapshot transactions")
        self.display_result(result, "Snapshot Transactions")

    def query_utxoset(self):
        """Snapshot UTXO Set 명령 실행"""
        result = self.handler.handle_query("snapshot utxoset")
        self.display_result(result, "Snapshot UTXO Set")

    def display_result(self, result, title):
        """결과를 GUI에 출력"""
        self.result_area.config(state=tk.NORMAL)
        self.result_area.insert(tk.END, f"=== {title} ===\n\n")  # 제목과 줄바꿈
        if isinstance(result, dict) and "error" in result:
            self.result_area.insert(tk.END, f"Error: {result['error']}\n\n")
        elif isinstance(result, list):
            for item in result:
                self.result_area.insert(tk.END, f"{item}\n\n")  # 각 항목 사이 줄바꿈
        else:
            self.result_area.insert(tk.END, f"{result}\n\n")
        self.result_area.insert(tk.END, "-" * 60 + "\n\n")  # 구분선과 줄바꿈
        self.result_area.config(state=tk.DISABLED)
        self.result_area.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = QueryGUI(root)
    root.mainloop()
