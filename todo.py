#!/usr/bin/env python3
"""
To-Do CLI v2.0 — Gerenciador de tarefas via linha de comando.

Uso:
  python todo.py add "Título" [--priority alta|media|baixa]
  python todo.py list [--pending|--done] [--priority alta|media|baixa]
  python todo.py toggle <id>
  python todo.py edit <id> [--title "novo título"] [--priority alta|media|baixa]
  python todo.py delete <id>
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

DATA_FILE = Path("tasks.json")

PRIORITIES = ["alta", "media", "baixa"]
PRIORITY_ORDER = {p: i for i, p in enumerate(PRIORITIES)}
PRIORITY_LABEL = {
    "alta":  "🔴 alta ",
    "media": "🟡 média",
    "baixa": "🟢 baixa",
}


def load() -> dict:
    """Carrega o arquivo de dados. Cria estrutura inicial se não existir."""
    if not DATA_FILE.exists():
        return {"next_id": 1, "tasks": []}
    try:
        with DATA_FILE.open("r", encoding="utf-8") as f:
            data = json.load(f)
        data.setdefault("next_id", 1)
        data.setdefault("tasks", [])
        # Migração v1 → v2: garante campo priority em tarefas antigas
        for t in data["tasks"]:
            t.setdefault("priority", "media")
        return data
    except (json.JSONDecodeError, ValueError):
        print("Erro: arquivo tasks.json corrompido. Iniciando com dados vazios.")
        return {"next_id": 1, "tasks": []}


def save(data: dict) -> None:
    """Persiste os dados no arquivo JSON."""
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)



def _format_date(iso: str) -> str:
    try:
        return datetime.fromisoformat(iso).strftime("%d/%m/%Y %H:%M")
    except ValueError:
        return iso


def _validate_title(title: str) -> str:
    """Valida e retorna título limpo, ou encerra com erro."""
    title = title.strip()
    if not title:
        print("Erro: o título não pode ser vazio.")
        sys.exit(1)
    if len(title) > 200:
        print("Erro: o título não pode ter mais de 200 caracteres.")
        sys.exit(1)
    return title


def _find_task(data: dict, task_id: int) -> dict:
    """Busca tarefa por ID ou encerra com erro."""
    task = next((t for t in data["tasks"] if t["id"] == task_id), None)
    if task is None:
        print(f"Erro: tarefa #{task_id} não encontrada.")
        sys.exit(1)
    return task


def _sort_tasks(tasks: list) -> list:
    """Ordena por prioridade (alta→baixa) e depois por ID crescente."""
    return sorted(tasks, key=lambda t: (PRIORITY_ORDER[t["priority"]], t["id"]))


def _print_tasks(tasks: list, total_data: dict) -> None:
    """Imprime tabela formatada de tarefas."""
    if not tasks:
        print("Nenhuma tarefa encontrada.")
        return

    print(f"\n{'ID':<5} {'Prioridade':<10} {'Status':<12} {'Criada em':<18} Título")
    print("─" * 75)
    for t in tasks:
        status = "✓ feita   " if t["done"] else "✗ pendente"
        created = _format_date(t["created_at"])
        priority = PRIORITY_LABEL[t["priority"]]
        print(f"#{t['id']:<4} {priority:<10} {status:<12} {created:<18} {t['title']}")

    all_tasks = total_data["tasks"]
    done = sum(1 for t in all_tasks if t["done"])
    print(f"\n{done}/{len(all_tasks)} concluída(s) no total | exibindo {len(tasks)} tarefa(s)\n")



def cmd_add(args: argparse.Namespace) -> None:
    """Adiciona nova tarefa com prioridade opcional."""
    title = _validate_title(args.title)
    data = load()

    task = {
        "id": data["next_id"],
        "title": title,
        "done": False,
        "priority": args.priority,
        "created_at": datetime.now().isoformat(timespec="seconds"),
    }
    data["tasks"].append(task)
    data["next_id"] += 1
    save(data)

    print(f"✅ Tarefa #{task['id']} adicionada [{task['priority']}]: \"{task['title']}\"")


def cmd_list(args: argparse.Namespace) -> None:
    """Lista tarefas com filtros combinados de status e prioridade."""
    data = load()
    tasks = data["tasks"]

    # Filtro de status
    if getattr(args, "pending", False):
        tasks = [t for t in tasks if not t["done"]]
    elif getattr(args, "done", False):
        tasks = [t for t in tasks if t["done"]]

    # Filtro de prioridade
    if args.priority:
        tasks = [t for t in tasks if t["priority"] == args.priority]

    tasks = _sort_tasks(tasks)
    _print_tasks(tasks, data)


def cmd_toggle(args: argparse.Namespace) -> None:
    """Inverte o status de conclusão de uma tarefa."""
    data = load()
    task = _find_task(data, args.id)
    task["done"] = not task["done"]
    save(data)

    status = "concluída ✓" if task["done"] else "pendente ✗"
    print(f"Tarefa #{task['id']} marcada como {status}: \"{task['title']}\"")


def cmd_edit(args: argparse.Namespace) -> None:
    """Edita título e/ou prioridade de uma tarefa existente."""
    # CA-11: ao menos um campo obrigatório
    if args.title is None and args.priority is None:
        print("Erro: informe --title e/ou --priority para editar.")
        sys.exit(1)

    data = load()
    task = _find_task(data, args.id)
    changes = []

    if args.title is not None:
        new_title = _validate_title(args.title)
        task["title"] = new_title
        changes.append(f"título → \"{new_title}\"")

    if args.priority is not None:
        task["priority"] = args.priority
        changes.append(f"prioridade → {args.priority}")

    save(data)
    print(f"✏️  Tarefa #{task['id']} atualizada: {' | '.join(changes)}")


def cmd_delete(args: argparse.Namespace) -> None:
    """Remove permanentemente uma tarefa."""
    data = load()
    task = _find_task(data, args.id)  # encerra se não existir

    data["tasks"] = [t for t in data["tasks"] if t["id"] != args.id]
    save(data)

    print(f"🗑️  Tarefa #{task['id']} excluída: \"{task['title']}\"")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="todo",
        description="📋 To-Do CLI v2 — gerencie suas tarefas no terminal.",
    )
    sub = parser.add_subparsers(dest="command", metavar="<comando>")
    sub.required = True

    # add
    p_add = sub.add_parser("add", help="Adiciona uma nova tarefa")
    p_add.add_argument("title", help="Título da tarefa")
    p_add.add_argument(
        "--priority", choices=PRIORITIES, default="media",
        metavar="PRIORIDADE", help="alta | media | baixa (padrão: media)"
    )
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = sub.add_parser("list", help="Lista as tarefas")
    status_group = p_list.add_mutually_exclusive_group()
    status_group.add_argument("--pending", action="store_true", help="Apenas pendentes")
    status_group.add_argument("--done", action="store_true", help="Apenas concluídas")
    p_list.add_argument(
        "--priority", choices=PRIORITIES, default=None,
        metavar="PRIORIDADE", help="Filtra por prioridade: alta | media | baixa"
    )
    p_list.set_defaults(func=cmd_list)

    # toggle
    p_toggle = sub.add_parser("toggle", help="Marca/desmarca tarefa como concluída")
    p_toggle.add_argument("id", type=int, help="ID da tarefa")
    p_toggle.set_defaults(func=cmd_toggle)

    # edit (novo)
    p_edit = sub.add_parser("edit", help="Edita título e/ou prioridade de uma tarefa")
    p_edit.add_argument("id", type=int, help="ID da tarefa")
    p_edit.add_argument("--title", default=None, help="Novo título")
    p_edit.add_argument(
        "--priority", choices=PRIORITIES, default=None,
        metavar="PRIORIDADE", help="Nova prioridade: alta | media | baixa"
    )
    p_edit.set_defaults(func=cmd_edit)

    # delete (novo)
    p_delete = sub.add_parser("delete", help="Exclui permanentemente uma tarefa")
    p_delete.add_argument("id", type=int, help="ID da tarefa")
    p_delete.set_defaults(func=cmd_delete)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()