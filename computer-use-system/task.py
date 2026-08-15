class Task:
    def __init__(
        self,
        member_id,
        account_type,
        initial_deposit,
    ):
        self.member_id = member_id
        self.account_type = account_type
        self.initial_deposit = initial_deposit


task = Task(
    member_id="12345",
    account_type="savings",
    initial_deposit="500",
)
