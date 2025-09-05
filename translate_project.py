#!/usr/bin/env python3
"""
Script to translate all Portuguese text to English in the Post Pilot project
"""

import os
import re

# Dictionary of translations
translations = {
    # Models and fields
    "Gerar Post Simples": "Generate Simple Post",
    "Gerar Artigo": "Generate Article",
    "Nenhum tópico gerado ainda": "No topics generated yet",
    'Clique em "Gerar Tópicos" para criar sugestões baseadas na descrição do tema.': 'Click "Generate Topics" to create suggestions based on the theme description.',
    "Posts Criados": "Created Posts",
    "Nenhum post criado ainda": "No posts created yet",
    "Criar Novo Tema": "Create New Theme",
    "Estatísticas do Tema": "Theme Statistics",
    "Posts Publicados": "Published Posts",
    "Status": "Status",
    "Criado:": "Created:",
    "Última atualização:": "Last update:",
    # Comments and descriptions
    "Formato novo estruturado": "New structured format",
    "Formato antigo simples": "Old simple format",
    "CTA sugerido:": "Suggested CTA:",
    # Messages and alerts
    "Task concluída! Recarregando página...": "Task completed! Reloading page...",
    "Task falhou:": "Task failed:",
    "Polling interrompido: tempo limite excedido": "Polling interrupted: time limit exceeded",
    "Erro no polling:": "Polling error:",
    "Mudanças detectadas! Recarregando página...": "Changes detected! Reloading page...",
    # Forms and buttons
    "Título": "Title",
    "Descrição": "Description",
    "Conteúdo": "Content",
    "Criar": "Create",
    "Salvar": "Save",
    "Cancelar": "Cancel",
    "Editar": "Edit",
    "Excluir": "Delete",
    "Publicar": "Publish",
    "Agendar": "Schedule",
    # Status values
    "Rascunho": "Draft",
    "Gerado": "Generated",
    "Publicado": "Published",
    "Agendado": "Scheduled",
    "Aguardando": "Waiting",
    "Processando": "Processing",
    "Concluído": "Completed",
    "Falhou": "Failed",
    # Date formats (basic replacement)
    "d/m/Y H:i": "m/d/Y H:i",
}


def translate_file(file_path):
    """Translate a single file"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        original_content = content

        # Apply translations
        for portuguese, english in translations.items():
            content = content.replace(portuguese, english)

        # Save if changed
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"✅ Updated: {file_path}")
        else:
            print(f"⚪ No changes: {file_path}")

    except Exception as e:
        print(f"❌ Error in {file_path}: {e}")


def main():
    """Main function to translate all files"""
    base_dir = "/home/rafael/workspace/post-pilot"

    # Files to translate
    files_to_translate = [
        # Templates
        "templates/core/theme_detail.html",
        "templates/core/theme_list.html",
        "templates/core/theme_create.html",
        "templates/core/post_list.html",
        "templates/core/post_detail.html",
        "templates/core/post_edit.html",
        "templates/core/dashboard.html",
        # Python files that might still have Portuguese
        "core/admin.py",
        "core/urls.py",
    ]

    print("🌐 TRANSLATING POST PILOT PROJECT TO ENGLISH")
    print("=" * 60)

    for file_path in files_to_translate:
        full_path = os.path.join(base_dir, file_path)
        if os.path.exists(full_path):
            translate_file(full_path)
        else:
            print(f"⚠️  File not found: {full_path}")

    print("\n🎉 Translation completed!")


if __name__ == "__main__":
    main()
