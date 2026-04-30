from flask import Flask, request, render_template
import redis
import pymysql

# 👇 aqui ajustamos para usar "template" (sem s)
app = Flask(__name__, template_folder="template")

# 🔴 Redis
redis_client = redis.Redis(
    host='xxx',
    port=xxx,
    password='xxx=',
    ssl=True,
    decode_responses=True
)

# 🟢 MariaDB (localhost)
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="SUA_SENHA_AQUI",
        database="testdb",
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    status = None

    if request.method == "POST":
        key = request.form.get("key")

        # 🔎 1. Busca no Redis
        cached_value = redis_client.get(key)

        if cached_value:
            result = cached_value
            status = "CACHE HIT"
        else:
            # 🔎 2. Busca no MariaDB
            conn = get_db_connection()
            try:
                with conn.cursor() as cursor:
                    sql = "SELECT valor FROM dados WHERE id = %s"
                    cursor.execute(sql, (key,))
                    row = cursor.fetchone()

                    if row:
                        result = row["valor"]

                        # 💾 salva no Redis
                        redis_client.set(key, result, ex=60)

                        status = "CACHE MISS (buscou no banco e salvou no cache)"
                    else:
                        result = "Valor não encontrado"
                        status = "NÃO ENCONTRADO"
            finally:
                conn.close()

    return render_template("index.html", result=result, status=status)


if __name__ == "__main__":
    app.run(debug=True)