from flask import Flask, request, render_template_string, redirect
import socket
import time
app = Flask(__name__)
# Stores domain and IP address
dns_cache = {}
# Stores previous searches
history = []
HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>DNS Resolver</title>
    <style>
        body {
            font-family: Arial;
            background: #f2f2f2;
            margin: 40px;
        }

        .box {
            background: white;
            width: 700px;
            margin: auto;
            padding: 25px;
            border-radius: 8px;
        }

        input {
            padding: 10px;
            width: 350px;
        }

        button {
            padding: 10px 15px;
            cursor: pointer;
        }

        .result {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #aaa;
            background: #fafafa;
        }

        .error {
            color: red;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }

        th, td {
            border: 1px solid #aaa;
            padding: 9px;
            text-align: left;
        }

        th {
            background: #eee;
        }

        .buttons {
            margin-top: 20px;
        }
    </style>
</head>
<body>
<div class="box">
    <h1>Domain to IP Address Resolver</h1>
    <p>
        This project demonstrates DNS resolution and DNS caching.
    </p>
    <form action="/resolve" method="POST">
        <input type="text" name="domain"placeholder="Enter domain "required>
        <button type="submit">Resolve</button>
    </form>
    {% if error %}

        <p class="error">{{ error }}</p>

    {% endif %}


    {% if result %}

        <div class="result">

            <h2>Resolution Result</h2>

            <p>
                <b>Domain:</b> {{ result.domain }}
            </p>

            <p>
                <b>IP Address:</b> {{ result.ip }}
            </p>

            <p>
                <b>Status:</b> {{ result.status }}
            </p>

            <p>
                <b>Response Time:</b> {{ result.time }} ms
            </p>

        </div>

    {% endif %}


    <div class="buttons">

        <form action="/clear-cache" method="POST"
              style="display:inline;">

            <button type="submit">
                Clear Cache
            </button>

        </form>


        <form action="/clear-history" method="POST"
              style="display:inline;">

            <button type="submit">
                Clear History
            </button>

        </form>

    </div>


    <h2>Search History</h2>

    {% if history %}

        <table>

            <tr>
                <th>Domain</th>
                <th>IP Address</th>
                <th>Status</th>
                <th>Time</th>
            </tr>

            {% for item in history %}

            <tr>

                <td>{{ item.domain }}</td>

                <td>{{ item.ip }}</td>

                <td>{{ item.status }}</td>

                <td>{{ item.time }} ms</td>

            </tr>

            {% endfor %}

        </table>

    {% else %}

        <p>No searches yet.</p>

    {% endif %}


    <h2>About DNS</h2>

    <p>
        DNS means Domain Name System. It converts a domain name
        such as google.com into an IP address.
    </p>

    <p>
        This application stores previously found IP addresses
        in a cache. When the same domain is searched again,
        the program can use the cached IP instead of performing
        another DNS lookup.
    </p>

</div>

</body>
</html>
"""


def clean_domain(domain):

    domain = domain.strip().lower()

    if domain.startswith("http://"):
        domain = domain[7:]

    elif domain.startswith("https://"):
        domain = domain[8:]

    domain = domain.split("/")[0]

    return domain


@app.route("/")
def home():

    return render_template_string(
        HTML,
        history=history
    )


@app.route("/resolve", methods=["POST"])
def resolve():

    domain = request.form.get("domain", "")

    domain = clean_domain(domain)

    if domain == "":
        return render_template_string(
            HTML,
            error="Please enter a domain name.",
            history=history
        )

    # Check whether the domain is already stored
    if domain in dns_cache:

        ip = dns_cache[domain]

        status = "CACHE HIT"

        response_time = 0

    else:

        start_time = time.time()

        try:

            # Perform DNS lookup
            ip = socket.gethostbyname(domain)

            end_time = time.time()

            response_time = round(
                (end_time - start_time) * 1000,
                2
            )

            status = "DNS LOOKUP"

            # Store the result
            dns_cache[domain] = ip

        except socket.gaierror:

            return render_template_string(
                HTML,
                error="Domain could not be found.",
                history=history
            )


    result = {
        "domain": domain,
        "ip": ip,
        "status": status,
        "time": response_time
    }

    # Add latest search at the beginning
    history.insert(0, result)

    return render_template_string(
        HTML,
        result=result,
        history=history
    )


@app.route("/clear-cache", methods=["POST"])
def clear_cache():

    dns_cache.clear()

    return redirect("/")


@app.route("/clear-history", methods=["POST"])
def clear_history():

    history.clear()

    return redirect("/")


if __name__ == "__main__":

    app.run(debug=True, port=5000)