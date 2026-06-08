# 📋 To-Do CLI v2.0

Evolução do To-Do CLI com edição, exclusão, prioridades e filtros combinados. Sem dependências externas — apenas Python 3.8+ stdlib.

---

## Instalação e uso rápido

```bash
git clone https://github.com/vitorsilvestre29/todo-cli.git
cd todo-cli
python todo.py --help
```

---

## Comandos

### `add` — Adicionar tarefa

```bash
python todo.py add "Título da tarefa"
python todo.py add "Título urgente" --priority alta
```

**Prioridades disponíveis:** `alta` | `media` (padrão) | `baixa`

```
✅ Tarefa #1 adicionada [media]: "Estudar Apache Iceberg"
```

---

### `list` — Listar tarefas

```bash
python todo.py list                          # todas, ordenadas por prioridade
python todo.py list --pending                # apenas pendentes
python todo.py list --done                   # apenas concluídas
python todo.py list --priority alta          # apenas alta prioridade
python todo.py list --pending --priority alta  # filtros combinados
```

```
ID    Prioridade Status       Criada em          Título
───────────────────────────────────────────────────────────────────────────
#2    🔴 alta     ✗ pendente   08/06/2026 14:30   Configurar Docker
#1    🟡 média    ✓ feita      08/06/2026 14:28   Estudar Apache Iceberg
#3    🟢 baixa    ✗ pendente   08/06/2026 14:31   Organizar desktop

1/3 concluída(s) no total | exibindo 3 tarefa(s)
```

---

### `toggle` — Marcar/desmarcar como concluída

```bash
python todo.py toggle <id>
```

```
Tarefa #1 marcada como concluída ✓: "Estudar Apache Iceberg"
```

---

### `edit` — Editar tarefa *(novo na v2)*

```bash
python todo.py edit <id> --title "Novo título"
python todo.py edit <id> --priority baixa
python todo.py edit <id> --title "Novo título" --priority alta
```

```
✏️  Tarefa #1 atualizada: título → "Novo título" | prioridade → alta
```

---

### `delete` — Excluir tarefa *(novo na v2)*

```bash
python todo.py delete <id>
```

```
🗑️  Tarefa #3 excluída: "Organizar desktop"
```

---

## Especificação Completa

### v1.0 — Especificação original

#### Descrição
Aplicação CLI em Python para gerenciamento pessoal de tarefas com persistência em JSON local.

#### Regras de Negócio

| ID | Regra |
|---|---|
| RN-01 | Cada tarefa recebe um ID inteiro único, sequencial e imutável |
| RN-02 | Campos obrigatórios: `id`, `title` (1–200 chars), `done` (default `false`), `created_at` (ISO 8601) |
| RN-03 | Dados persistem em `tasks.json`, criado automaticamente se não existir |
| RN-04 | `toggle` inverte o estado atual (`false → true` ou `true → false`) |
| RN-05 | Título vazio ou só espaços é rejeitado com erro e exit code 1 |
| RN-06 | Operações em IDs inexistentes retornam erro e exit code 1 |

#### Critérios de Aceite v1

| ID | Critério | Status |
|---|---|---|
| CA-01 | `add` válido persiste e exibe confirmação com ID | ✅ |
| CA-02 | `add` vazio retorna erro sem criar tarefa | ✅ |
| CA-03 | `list` vazio exibe "Nenhuma tarefa encontrada" | ✅ |
| CA-04 | `list` exibe ID, status, data e título | ✅ |
| CA-05 | `toggle` inverte status e confirma | ✅ |
| CA-06 | `toggle` em ID inexistente retorna erro e exit code 1 | ✅ |
| CA-07 | `tasks.json` criado automaticamente | ✅ |
| CA-08 | IDs únicos e não reutilizados | ✅ |

---

### v2.0 — Evolução do sistema

#### O que mudou

| Funcionalidade | v1 | v2 |
|---|---|---|
| Adicionar tarefa | ✅ | ✅ + suporte a `--priority` |
| Listar tarefas | ✅ básico | ✅ ordenado por prioridade + filtro combinado |
| Toggle concluída | ✅ | ✅ mantido |
| **Editar tarefa** | ❌ | ✅ novo |
| **Excluir tarefa** | ❌ | ✅ novo |
| **Prioridade** | ❌ | ✅ alta / media / baixa |
| **Filtro por prioridade** | ❌ | ✅ combinável com status |
| Validação título vazio | ✅ na criação | ✅ também na edição |
| Persistência JSON | ✅ | ✅ modelo expandido + migração automática v1→v2 |

#### Novas Regras de Negócio

| ID | Regra |
|---|---|
| RN-07 | Toda tarefa tem prioridade: `alta`, `media` ou `baixa`. Default na criação: `media`. Listagem ordenada por prioridade (alta→baixa) e depois por ID crescente |
| RN-08 | `edit` permite alterar título e/ou prioridade. Ao menos um campo é obrigatório. Validações de criação aplicam-se ao título editado |
| RN-09 | `delete` remove permanentemente a tarefa. ID não é reutilizado. Operação é irreversível |
| RN-10 | `list` aceita `--priority alta|media|baixa` combinável com `--pending` ou `--done` |
| RN-11 | Migração automática: tarefas criadas na v1 (sem campo `priority`) recebem `"media"` ao serem carregadas pela v2, sem intervenção manual |

#### Critérios de Aceite v2

| ID | Critério | Status |
|---|---|---|
| CA-09 | `edit <id> --title "novo"` atualiza o título e confirma | ✅ |
| CA-10 | `edit <id> --priority alta` atualiza só a prioridade | ✅ |
| CA-11 | `edit` sem `--title` nem `--priority` retorna erro | ✅ |
| CA-12 | `delete <id>` remove a tarefa e confirma com nome | ✅ |
| CA-13 | `delete` em ID inexistente retorna erro e exit code 1 | ✅ |
| CA-14 | `add` sem `--priority` cria com prioridade `media` | ✅ |
| CA-15 | `list` ordena por prioridade (alta primeiro), depois por ID | ✅ |
| CA-16 | `list --priority alta` filtra apenas tarefas de alta prioridade | ✅ |
| CA-17 | Filtros `--priority` e `--pending/--done` são combináveis | ✅ |

---

### Modelo de dados v2 (`tasks.json`)

```json
{
  "next_id": 4,
  "tasks": [
    {
      "id": 1,
      "title": "Estudar Apache Iceberg",
      "done": true,
      "priority": "alta",
      "created_at": "2026-06-08T14:28:00"
    },
    {
      "id": 2,
      "title": "Configurar Docker",
      "done": false,
      "priority": "media",
      "created_at": "2026-06-08T14:30:00"
    }
  ]
}
```

**Campo adicionado em relação à v1:** `"priority": "alta" | "media" | "baixa"`

---

### Impacto da evolução no sistema original

**O que foi preservado sem alteração:**
- Interface dos comandos `add`, `list`, `toggle` (retrocompatível)
- Formato do `tasks.json` (campo `priority` é adicionado via migração automática)
- Todas as regras de validação da v1

**O que foi estendido:**
- `add` ganhou `--priority` opcional
- `list` ganhou ordenação por prioridade e `--priority` como filtro adicional
- `load()` aplica migração silenciosa em dados da v1

**O que foi adicionado sem impacto nos existentes:**
- `edit` e `delete` são comandos novos, não conflitam com nada anterior

---

## Como a especificação influenciou o desenvolvimento com IA

Este projeto foi desenvolvido com apoio de IA (Claude). A qualidade da especificação teve impacto direto nos resultados:

### Especificação detalhada → menos retrabalho

A definição prévia de regras de negócio numeradas (RN-XX) e critérios de aceite mensuráveis (CA-XX) permitiu que a IA gerasse código já alinhado com os requisitos na primeira tentativa. Todos os 17 critérios de aceite foram validados automaticamente via testes no terminal antes da entrega.

### O que teria saído diferente sem especificação

Sem a RN-11 (migração automática v1→v2), a IA provavelmente geraria código que quebraria ao ler um `tasks.json` da versão anterior — um problema real de retrocompatibilidade que só foi evitado porque estava explícito na especificação.

Sem a RN-07 definindo a ordenação, a listagem provavelmente retornaria tarefas na ordem de inserção (comportamento padrão de lista), não por prioridade.

### Lição prática

Especificação ambígua → IA preenche lacunas com suposições que podem não ser as suas. Especificação com critérios de aceite objetivos → a saída é verificável e previsível. A IA é mais útil como executor de uma especificação clara do que como definidora de requisitos.

---

## Estrutura do projeto

```
todo-cli/
├── todo.py      # Aplicação principal (v2.0)
├── .gitignore
└── README.md
```

---

## Requisitos

- Python 3.8+
- Sem dependências externas

---

## Changelog

### v2.0
- Adicionado: comando `edit` (título e/ou prioridade)
- Adicionado: comando `delete`
- Adicionado: campo `priority` (alta/media/baixa) em todas as tarefas
- Adicionado: `--priority` como filtro em `list`
- Adicionado: ordenação por prioridade na listagem
- Adicionado: migração automática de dados da v1
- Melhorado: validação de título aplicada também na edição

### v1.0
- Comandos: `add`, `list`, `toggle`
- Persistência em `tasks.json`
- Filtros `--pending` e `--done`

---

## Licença

MIT