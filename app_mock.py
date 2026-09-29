from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><title>Legacy Bank Back-Office Console</title></head>
<body style="font-family: sans-serif; padding: 20px;">
    <h2>Legacy Bank Core Servicing Portal</h2>
    <div id="search-section">
        <label for="member-input">Member ID Search:</label>
        <input type="text" id="member-input" name="memberSearch" data-testid="member-search-input" />
        <button id="btn-search" onclick="searchMember()">Search</button>
    </div>
    <hr/>
    <div id="results-section" style="display:none;">
        <h3>Member Details</h3>
        <p><strong>Member ID:</strong> <span id="res-id"></span></p>
        <p><strong>Savings Balance:</strong> $<span id="savings-val" data-testid="savings-val">12450.50</span></p>
        <p><strong>Status:</strong> <span id="account-status">ACTIVE</span></p>
    </div>
    <div id="error-section" style="display:none; color: red;">
        <p id="error-msg" data-testid="error-message">Error: Member Not Found</p>
    </div>

    <script>
        function searchMember() {
            const val = document.getElementById('member-input').value;
            if (val === "12345") {
                document.getElementById('res-id').innerText = val;
                document.getElementById('results-section').style.display = 'block';
                document.getElementById('error-section').style.display = 'none';
            } else {
                document.getElementById('results-section').style.display = 'none';
                document.getElementById('error-section').style.display = 'block';
            }
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    return render_template_string(HTML_TEMPLATE)

if __name__ == "__main__":
    app.run(port=5000)