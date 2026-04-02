import uuid
from django.core.cache import cache
from .userClass import User


TXN_PREFIX = "txn:"
TXN_LIST_KEY = "txn_list"
DATA_TIMEOUT = 3600  # 1 hour



class Transaction:
    VALID_TYPES = {"income", "expense"}

    def __init__(self, amount, t_type, category, notes="", tid=None):
        if amount <= 0:
            raise ValueError("Amount must be positive")

        if t_type not in self.VALID_TYPES:
            raise ValueError("Invalid transaction type")

        self.tid = tid or str(uuid.uuid4())
        self.amount = amount
        self.type = t_type
        self.category = category
        self.notes = notes

    def update(self, amount=None, t_type=None, category=None, notes=None):
        if amount is not None:
            if amount <= 0:
                raise ValueError("Invalid amount")
            self.amount = amount

        if t_type is not None:
            if t_type not in self.VALID_TYPES:
                raise ValueError("Invalid type")
            self.type = t_type

        if category is not None:
            self.category = category

        if notes is not None:
            self.notes = notes

    def to_dict(self):
        return {
            "tid": self.tid,
            "amount": self.amount,
            "type": self.type,
            "category": self.category,
            "notes": self.notes
        }

    @staticmethod
    def from_dict(data):
        return Transaction(
            amount=data["amount"],
            t_type=data["type"],
            category=data["category"],
            notes=data.get("notes", ""),
            tid=data["tid"]
        )
        

def has_access(user:User, action):
    if user.isMasterAdmin():
        return True

    if action == "read":
        return user.isViewer() or user.isAnalyst() or user.isTransactionAdmin()

    if action == "insight":
        return user.isAnalyst() or user.isTransactionAdmin()

    if action == "write":
        return user.isTransactionAdmin()

    return False

class TransactionService:
    
    @staticmethod
    def addTransaction(request_user:User, amount, t_type, category, notes=""):
        if not has_access(request_user, "write"):
            raise PermissionError("Only Transaction Admins or Master Admins are allowed to add transactions")

        txn = Transaction(amount, t_type, category, notes)

        cache.set(f"{TXN_PREFIX}{txn.tid}", txn.to_dict(), timeout=DATA_TIMEOUT)

        txn_list = cache.get(TXN_LIST_KEY, [])
        txn_list.append(txn.tid)
        cache.set(TXN_LIST_KEY, txn_list, timeout=DATA_TIMEOUT)

        return txn
    
    @staticmethod
    def updateTransaction(request_user:User, tid, **kwargs):
        if not has_access(request_user, "write"):
            raise PermissionError("Only Transaction Admins or Master Admins are allowed to update transactions")

        data = cache.get(f"{TXN_PREFIX}{tid}")
        if not data:
            raise ValueError("Transaction not found")

        txn = Transaction.from_dict(data)
        txn.update(**kwargs)

        cache.set(f"{TXN_PREFIX}{tid}", txn.to_dict(), timeout=DATA_TIMEOUT)

        return txn
    
    @staticmethod
    def deleteTransaction(request_user:User, tid):
        if not has_access(request_user, "write"):
            raise PermissionError("Only Transaction Admins or Master Admins are allowed to update transactions")

        data = cache.get(f"{TXN_PREFIX}{tid}")
        if not data:
            raise ValueError("Transaction not found")

        cache.delete(f"{TXN_PREFIX}{tid}")

        txn_list = cache.get(TXN_LIST_KEY, [])
        txn_list = [x for x in txn_list if x != tid]
        cache.set(TXN_LIST_KEY, txn_list, timeout=DATA_TIMEOUT)

        return True
    
    @staticmethod
    def getTransaction(request_user, page=0, limit=10, filters=None):
        if not has_access(request_user, "read"):
            raise PermissionError("Only Viewers, Analysts, or Transaction Admins/Master Admins are allowed to view transactions")

        txn_list = cache.get(TXN_LIST_KEY, [])
        txns = []

        for tid in txn_list:
            data = cache.get(f"{TXN_PREFIX}{tid}")
            if data:
                txns.append(data)

        # Filtering
        if filters:
            if "type" in filters:
                txns = [t for t in txns if t["type"] == filters["type"]]

            if "category" in filters:
                txns = [t for t in txns if t["category"] == filters["category"]]

        # Pagination
        start = page * limit
        end = start + limit

        return txns[start:end]
    
    @staticmethod
    def getInsights(request_user):
        if not has_access(request_user, "insight"):
            raise PermissionError("Only Analysts or Transaction Admins/Master Admins are allowed to view transaction insights")

        txn_list = cache.get(TXN_LIST_KEY, [])

        total_income = 0
        total_expense = 0
        category_total = {}

        recent = []

        for tid in txn_list:  
            data = cache.get(f"{TXN_PREFIX}{tid}")
            if not data:
                continue

            amt = data["amount"]
            cat = data["category"]

            if data["type"] == "income":
                total_income += amt
            else:
                total_expense += amt

            category_total[cat] = category_total.get(cat, 0) + amt
        
        for tid in txn_list[-10:]:
            data = cache.get(f"{TXN_PREFIX}{tid}")
            if data:
                recent.append(data)


        net_balance = total_income - total_expense
        

        # top category
        top_category = max(category_total, key=category_total.get, default=None)

        return {
            "totalIncome": total_income,
            "totalExpense": total_expense,
            "netBalance": net_balance,
            "categoryTotal": category_total,
            "recentAct": recent,
            "topCategory": top_category
        }