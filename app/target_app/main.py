from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

app = FastAPI(title="Bank Operations Portal")


# Fake member data for our local demo application
MEMBERS = {
    "12345": {
        "name": "John Smith",
        "savings_balance": "4250.00",
        "checking_balance": "1200.00",
    },
    "67890": {
        "name": "Sarah Johnson",
        "savings_balance": "8100.50",
        "checking_balance": "2500.00",
    },
}


@app.get("/", response_class=HTMLResponse)
def login_page():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bank Operations Portal</title>
    </head>

    <body>
        <h1>Bank Operations Portal</h1>

        <form method="post" action="/login">
            <label for="username">Username:</label>
            <input id="username" name="username" type="text">

            <br><br>

            <label for="password">Password:</label>
            <input id="password" name="password" type="password">

            <br><br>

            <button type="submit">Login</button>
        </form>
    </body>
    </html>
    """


@app.post("/login", response_class=HTMLResponse)
def login(username: str = Form(...), password: str = Form(...)):
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Member Search</title>
    </head>

    <body>
        <h1>Member Search</h1>

        <form method="post" action="/search">
            <label for="member_id">Member ID:</label>
            <input id="member_id" name="member_id" type="text">

            <button type="submit">Search</button>
        </form>
    </body>
    </html>
    """


@app.post("/search", response_class=HTMLResponse)
def search_member(member_id: str = Form(...)):
    member = MEMBERS.get(member_id)

    if member is None:
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>Member Search</title>
        </head>

        <body>
            <h1>Member Search</h1>

            <p>Member {member_id} was not found.</p>

            <a href="/">Return to login</a>
        </body>
        </html>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Member Details</title>
    </head>

    <body>
        <h1>Member Details</h1>

        <p><strong>Member ID:</strong> {member_id}</p>
        <p><strong>Name:</strong> {member["name"]}</p>
        <p><strong>Savings Balance:</strong> ${member["savings_balance"]}</p>
        <p><strong>Checking Balance:</strong> ${member["checking_balance"]}</p>

        <br>

        <form method="get" action="/sub-account">
            <input type="hidden" name="member_id" value="{member_id}">
            <button type="submit">Open Sub-Account</button>
        </form>
    </body>
    </html>
    """


@app.get("/sub-account", response_class=HTMLResponse)
def sub_account_page(member_id: str):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Open Sub-Account</title>
    </head>

    <body>
        <h1>Open New Sub-Account</h1>

        <p><strong>Member ID:</strong> {member_id}</p>

        <form method="post" action="/sub-account">
            <input type="hidden" name="member_id" value="{member_id}">

            <label for="account_type">Account Type:</label>

            <select id="account_type" name="account_type">
                <option value="savings">Savings</option>
                <option value="checking">Checking</option>
            </select>

            <br><br>

            <label for="initial_deposit">Initial Deposit:</label>

            <input
                id="initial_deposit"
                name="initial_deposit"
                type="number"
                step="0.01"
                min="0"
            >

            <br><br>

            <button type="submit">Continue</button>
        </form>
    </body>
    </html>
    """


@app.post("/sub-account", response_class=HTMLResponse)
def create_sub_account(
    member_id: str = Form(...),
    account_type: str = Form(...),
    initial_deposit: float = Form(...),
):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Review Sub-Account</title>
    </head>

    <body>
        <h1>Review New Sub-Account</h1>

        <p><strong>Member ID:</strong> {member_id}</p>
        <p><strong>Account Type:</strong> {account_type.title()}</p>
        <p><strong>Initial Deposit:</strong> ${initial_deposit:.2f}</p>

        <br>

        <p>Please review the information above.</p>

        <form method="post" action="/sub-account/confirm">
            <input type="hidden" name="member_id" value="{member_id}">
            <input type="hidden" name="account_type" value="{account_type}">
            <input type="hidden" name="initial_deposit" value="{initial_deposit}">

            <button type="submit">Confirm</button>
        </form>

        <a href="/sub-account?member_id={member_id}">Cancel</a>
    </body>
    </html>
    """


@app.post("/sub-account/confirm", response_class=HTMLResponse)
def confirm_sub_account(
    member_id: str = Form(...),
    account_type: str = Form(...),
    initial_deposit: float = Form(...),
):
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Account Created</title>
    </head>

    <body>
        <h1>Sub-Account Created Successfully</h1>

        <p>
            <strong>Member ID:</strong> {member_id}
        </p>

        <p>
            <strong>Account Type:</strong> {account_type.title()}
        </p>

        <p>
            <strong>Initial Deposit:</strong> ${initial_deposit:.2f}
        </p>

        <p>
            <strong>Status:</strong> Created
        </p>
    </body>
    </html>
    """
