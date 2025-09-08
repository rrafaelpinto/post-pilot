#!/usr/bin/env python3
"""
Script de teste para a API do Post Pilot
Demonstra como usar os principais endpoints da API
"""

import requests
import json
import time
from datetime import datetime

# Configurações
BASE_URL = "http://localhost:8000/api"
HEADERS = {"Content-Type": "application/json"}


def print_response(response, title="Response"):
    """Imprime resposta formatada"""
    print(f"\n{'=' * 50}")
    print(f"{title}")
    print(f"{'=' * 50}")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")


def wait_for_task(task_id, max_wait=60):
    """Aguarda conclusão de uma task"""
    print(f"\n⏳ Aguardando task {task_id}...")
    start_time = time.time()

    while time.time() - start_time < max_wait:
        response = requests.get(f"{BASE_URL}/tasks/check/", params={"task_id": task_id})
        if response.status_code == 200:
            data = response.json()
            state = data.get("state")
            print(f"Status: {state}")

            if state == "SUCCESS":
                print("✅ Task concluída com sucesso!")
                return data
            elif state == "FAILURE":
                print("❌ Task falhou!")
                return data
            elif state in ["PENDING", "STARTED"]:
                time.sleep(2)
                continue

        time.sleep(2)

    print("⏰ Timeout aguardando task")
    return None


def test_dashboard():
    """Testa endpoint do dashboard"""
    print("\n🏠 Testando Dashboard")
    response = requests.get(f"{BASE_URL}/dashboard/stats/")
    print_response(response, "Dashboard Stats")
    return response.json() if response.status_code == 200 else None


def test_create_theme():
    """Testa criação de tema"""
    print("\n🎨 Testando Criação de Tema")
    data = {"title": f"Teste API - {datetime.now().strftime('%H:%M:%S')}"}
    response = requests.post(f"{BASE_URL}/themes/", json=data, headers=HEADERS)
    print_response(response, "Criar Tema")
    return response.json() if response.status_code == 201 else None


def test_generate_topics(theme_id):
    """Testa geração de tópicos"""
    print(f"\n🧠 Testando Geração de Tópicos para Tema {theme_id}")
    response = requests.post(
        f"{BASE_URL}/themes/{theme_id}/generate_topics/", headers=HEADERS
    )
    print_response(response, "Gerar Tópicos")

    if response.status_code == 200:
        data = response.json()
        task_id = data.get("task_id")
        if task_id:
            # Aguarda conclusão
            task_result = wait_for_task(task_id)

            # Verifica tópicos gerados
            theme_response = requests.get(f"{BASE_URL}/themes/{theme_id}/")
            if theme_response.status_code == 200:
                theme_data = theme_response.json()
                topics = theme_data.get("suggested_topics", {}).get("topics", [])
                print(f"\n📝 Tópicos gerados ({len(topics)}):")
                for i, topic in enumerate(
                    topics[:3], 1
                ):  # Mostra apenas os 3 primeiros
                    print(f"  {i}. {topic}")

            return theme_data if theme_response.status_code == 200 else None

    return None


def test_generate_post(theme_id, topic):
    """Testa geração de post"""
    print(f"\n📝 Testando Geração de Post")
    data = {"topic": topic, "post_type": "simple"}
    response = requests.post(
        f"{BASE_URL}/themes/{theme_id}/generate_post/", json=data, headers=HEADERS
    )
    print_response(response, "Gerar Post")

    if response.status_code == 200:
        data = response.json()
        task_id = data.get("task_id")
        if task_id:
            # Aguarda conclusão
            task_result = wait_for_task(task_id)

            # Lista posts do tema para encontrar o novo
            posts_response = requests.get(f"{BASE_URL}/themes/{theme_id}/posts/")
            if posts_response.status_code == 200:
                posts = posts_response.json()
                print(f"\n📋 Posts do tema ({len(posts)}):")
                for post in posts[:2]:  # Mostra apenas os 2 primeiros
                    title = post.get("title", "Sem título")
                    status = post.get("status", "unknown")
                    print(f"  - {title} (Status: {status})")

                # Retorna o primeiro post para testes adicionais
                return posts[0] if posts else None

    return None


def test_improve_post(post_id):
    """Testa melhoria de post"""
    print(f"\n✨ Testando Melhoria de Post {post_id}")
    response = requests.post(f"{BASE_URL}/posts/{post_id}/improve/", headers=HEADERS)
    print_response(response, "Melhorar Post")

    if response.status_code == 200:
        data = response.json()
        task_id = data.get("task_id")
        if task_id:
            task_result = wait_for_task(task_id)
            return task_result

    return None


def test_publish_post(post_id):
    """Testa publicação de post"""
    print(f"\n🚀 Testando Publicação de Post {post_id}")
    response = requests.post(f"{BASE_URL}/posts/{post_id}/publish/", headers=HEADERS)
    print_response(response, "Publicar Post")
    return response.json() if response.status_code == 200 else None


def test_list_posts():
    """Testa listagem de posts"""
    print("\n📋 Testando Listagem de Posts")
    response = requests.get(f"{BASE_URL}/posts/")
    print_response(response, "Listar Posts")
    return response.json() if response.status_code == 200 else None


def main():
    """Executa todos os testes"""
    print("🧪 Iniciando Testes da API Post Pilot")
    print(f"Base URL: {BASE_URL}")

    try:
        # 1. Dashboard
        test_dashboard()

        # 2. Criar tema
        theme = test_create_theme()
        if not theme:
            print("❌ Falha ao criar tema. Abortando testes.")
            return

        theme_id = theme["id"]

        # 3. Gerar tópicos
        theme_with_topics = test_generate_topics(theme_id)
        if not theme_with_topics:
            print("❌ Falha ao gerar tópicos. Continuando sem tópicos...")
            topic = "Teste manual de tópico"
        else:
            topics = theme_with_topics.get("suggested_topics", {}).get("topics", [])
            topic = topics[0] if topics else "Teste manual de tópico"

        # 4. Gerar post
        post = test_generate_post(theme_id, topic)
        if post:
            post_id = post["id"]

            # 5. Melhorar post (opcional - pode demorar)
            # test_improve_post(post_id)

            # 6. Publicar post
            test_publish_post(post_id)

        # 7. Listar posts finais
        test_list_posts()

        print("\n✅ Testes concluídos!")

    except requests.exceptions.ConnectionError:
        print(
            "❌ Erro de conexão. Verifique se o servidor está rodando em http://localhost:8000"
        )
    except KeyboardInterrupt:
        print("\n⏹️ Testes interrompidos pelo usuário")
    except Exception as e:
        print(f"❌ Erro inesperado: {e}")


if __name__ == "__main__":
    main()
