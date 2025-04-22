import requests

NOTION_API_KEY = "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"
NOTION_DATABASE_ID = "1bbb39fb6eed80449929c77ee2445d41"
NOTION_VERSION = "2022-06-28"

url = f"https://api.notion.com/v1/databases/{NOTION_DATABASE_ID}/query"

headers = {
    "Authorization": f"Bearer {NOTION_API_KEY}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

response = requests.post(url, headers=headers)

if response.status_code == 200:
    data = response.json()
    print("\n✅ Conexão com o Notion OK! Resultados encontrados:\n")
    for i, result in enumerate(data["results"]):
        props = result["properties"]
        pergunta = props.get("Pergunta", {}).get("title", [{}])[0].get("text", {}).get("content", "Sem conteúdo")
        resposta = props.get("Resposta", {}).get("rich_text", [{}])[0].get("text", {}).get("content", "Sem conteúdo")
        print(f"{i+1}. {pergunta} ➜ {resposta}")
else:
    print("❌ Erro ao conectar com o Notion.")
    print("Status:", response.status_code)
    print("Resposta:", response.text)
