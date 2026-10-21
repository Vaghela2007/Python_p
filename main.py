"""PTMAE demo solution"""

class BaseSystemError(Exception):
    pass


class CorruptedRecordError(BaseSystemError):
    pass


class OutOfBoundsError(BaseSystemError):
    pass


class InsufficientBalanceError(BaseSystemError):
    pass


# ---------- Unit 1 ----------
def compound_interest(principal, rate, years):
    amount = principal
    i = 0
    while i < years:
        amount = amount + amount * rate / 100
        i += 1
    return amount - principal


def penalty_fee(base_fee, days_late):
    fee = 0
    d = 0
    while d < days_late:
        fee = fee + base_fee * (1 + d // 7)
        d += 1
    return fee % 10000 ** 1


def trajectory_guard(balance, transactions, threshold):
    for t in transactions:
        if t == "STOP" or balance < threshold:
            break
        balance += t
    return balance


def interactive_loop():
    running = True
    while running:
        cmd = input("ptmae> ").strip()
        while cmd == "":
            cmd = input("ptmae> ").strip()
        if cmd == "exit":
            break
        print("unknown command:", cmd)


# ---------- Unit 2 ----------
def parse_raw_log_line(line, delimiter=",", quote_char='"'):
    tokens = []
    field = ""
    in_quotes = False
    i = 0
    n = len(line)
    while i < n:
        ch = line[i]
        nxt = line[i + 1:i + 2]
        if in_quotes:
            if ch == quote_char and nxt == quote_char:
                field += quote_char
                i += 1
            elif ch == quote_char:
                in_quotes = False
            else:
                field += ch
        elif ch == quote_char:
            in_quotes = True
        elif ch == delimiter:
            tokens.append(field)
            field = ""
        else:
            field += ch
        i += 1
    tokens.append(field)
    return tokens


def create_audit_filter(threshold):
    audited = 0

    def validate(amount):
        nonlocal audited
        audited += 1
        return amount >= threshold

    return validate


def build_filters(n):
    filters = []
    for k in range(n):
        filters.append(lambda row, k=k: row[k] > 0)
    return filters


# ---------- Unit 3 ----------
raw_db = {
    "BRANCH_01": [("Acc101", {"DEPOSIT", "UPI"}), ("Acc102", {"LOAN", "UPI"})],
    "BRANCH_02": [("Acc101", {"SAVINGS", "UPI"}), ("Acc103", {"CARD", "DEPOSIT"})],
}

reverse_index = {tag: sorted({(acc, br) for br, rows in raw_db.items() for acc, tags in rows if tag in tags}) for tag in {t for rows in raw_db.values() for _, tags in rows for t in tags}}


def clean_transaction_queue(data_list):
    for i in range(len(data_list)):
        item = data_list[i]
        if isinstance(item, tuple):
            item = list(item)
            data_list[i] = item
        if isinstance(item, set):
            evens = {x for x in item if x % 2 == 0}
            item -= evens
        elif isinstance(item, list):
            item.sort(reverse=True)
    i = 0
    while i < len(data_list):
        v = data_list[i]
        dup = False
        if isinstance(v, int):
            for j in range(i):
                if isinstance(data_list[j], int) and data_list[j] == v:
                    dup = True
                    break
        if dup:
            del data_list[i]
        else:
            i += 1


# ---------- Unit 4 ----------
def update_record(path, account_id, new_balance):
    processed, rejected = 0, 0
    try:
        with open(path, "r+") as f:
            line_no = 0
            while True:
                pos = f.tell()
                line = f.readline()
                if not line:
                    break
                line_no += 1
                parts = parse_raw_log_line(line.strip())
                if len(parts) != 3:
                    rejected += 1
                    with open("corrupted.log", "a") as log:
                        log.write("line " + str(line_no) + ": " + line)
                    continue
                if parts[0] == account_id:
                    new_line = parts[0] + "," + parts[1] + "," + str(new_balance) + "\n"
                    rest = f.read()
                    f.seek(pos)
                    f.write(new_line + rest)
                    f.truncate()
                    processed += 1
                    break
    except OSError as e:
        raise CorruptedRecordError(str(e))
    else:
        with open("ledger.txt", "a") as led:
            led.write(account_id + " -> " + str(new_balance) + "\n")
    finally:
        print("Processed:", processed, "Rejected:", rejected)


# ---------- Unit 5 ----------
class Account:
    total_accounts = 0

    def __init__(self, account_id, balance):
        self._account_id = account_id
        self.__balance = 0
        self.set_balance(balance)
        Account.total_accounts += 1

    def get_balance(self):
        return self.__balance

    def set_balance(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("balance must be numeric")
        self.__balance = value

    def process_settlement(self, amount):
        raise NotImplementedError


class SavingsAccount(Account):
    def __init__(self, account_id, balance):
        super().__init__(account_id, balance)

    def process_settlement(self, amount):
        if self.get_balance() - amount < 1000:
            raise InsufficientBalanceError("below minimum 1000")
        self.set_balance(self.get_balance() - amount)


class CurrentAccount(Account):
    def __init__(self, account_id, balance, limit):
        super().__init__(account_id, balance)
        self.__overdraft_limit = limit

    def process_settlement(self, amount):
        if self.get_balance() - amount < -self.__overdraft_limit:
            raise OutOfBoundsError("overdraft exceeded")
        self.set_balance(self.get_balance() - amount)


class CreditAccount(Account):
    def __init__(self, account_id, balance, limit):
        super().__init__(account_id, balance)
        self.__credit_limit = limit

    def process_settlement(self, amount):
        total = amount * 1.025
        if total > self.__credit_limit:
            raise OutOfBoundsError("credit limit exceeded")
        self.__credit_limit -= total


def execute_batch_settlement(account_list, transaction_amount):
    ok, failed = 0, 0
    for acc in account_list:
        try:
            acc.process_settlement(transaction_amount)
        except BaseSystemError:
            failed += 1
        else:
            ok += 1
    return ok, failed


if __name__ == "__main__":
    a = SavingsAccount("S1", 5000)
    print(a._Account__balance)
    print(execute_batch_settlement([a, CurrentAccount("C1", 100, 500), CreditAccount("R1", 0, 10000)], 800))
