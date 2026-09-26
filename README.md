# Engineering

A collection of Claude skills for project management and construction management.

- **`construction-management/`**: custom skills written for this repo. They cover scheduling, estimating, earned value, claims, FIDIC/NEC contract administration, RFIs and submittals, and HSE and quality. See [construction-management/README.md](construction-management/README.md).
- **`combined-skill/`**: all 26 skills bundled into **one** Claude skill (`construction-project-management`), with a single entry point that routes each request to the right module. To install it, upload `combined-skill/construction-project-management.zip` in claude.ai under **Settings → Capabilities → Skills**. The unpacked source is in the folder beside the zip.
- **Everything else** was collected from [alirezarezvani/claude-skills](https://github.com/alirezarezvani/claude-skills) under the MIT License (see `THIRD_PARTY_LICENSE`).

The folder layout matches the source repo, so paths inside the skills (for example `project-management/skills/scrum-master/...`) still work when you run commands from the repo root.

## Project management (`project-management/`)

This is a complete plugin, including its agents, commands and references.

| Skill | Use it for |
|---|---|
| `senior-pm` | Project charters, RACI, risk registers (EMV, Monte Carlo), resource capacity planning, portfolio health, executive reports |
| `scrum-master` | Sprint planning, velocity forecasting, burndown, retrospectives, team health scoring |
| `pm-skills` | An orchestrator that routes a request to the right PM sub-skill and can run a full plan → execute → verify → close delivery loop |
| `jira-expert` | Setting up Jira projects, JQL, workflows, dashboards and automation |
| `confluence-expert` | Confluence spaces, page hierarchies, documentation templates |
| `atlassian-admin` | Users, permissions, SSO and governance across Jira and Confluence |
| `atlassian-templates` | Reusable Jira and Confluence templates and blueprints |
| `meeting-analyzer` | Analysis of meeting transcripts and coaching on how meetings are run |
| `team-communications` | Status reports, 3P updates, leadership updates, incident reports |

## Contracts, bidding & procurement

| Skill | Path | Use it for |
|---|---|---|
| `rfp-responder` | `commercial/skills/rfp-responder` | Responding to RFPs, RFIs and RFQs: requirement matrix, win themes, bid/no-bid decision |
| `contract-and-proposal-writer` | `business-growth/skills/contract-and-proposal-writer` | Drafting proposals, SOWs, contracts and NDAs |
| `procurement-optimizer` | `business-operations/skills/procurement-optimizer` | Spend categorisation, supplier rationalisation, purchasing-cycle bottlenecks |

## Supporting dependency

- `engineering/agent-harness`: the loop engine that `pm-skills` calls in its "delivery loop" mode. It isn't needed for the other skills.

## Notes

- The source repo has no construction-specific skills. That gap is covered by the custom skills in `construction-management/`.
- Several scripts need Python 3 (`python3 <skill>/scripts/<script>.py --help`).

## Using these skills in Claude Code

- **As a plugin:** `project-management/.claude-plugin` lets you install that folder as a Claude Code plugin.
- **As personal skills:** copy any skill folder (the one containing `SKILL.md`) into `~/.claude/skills/`, or into `.claude/skills/` inside a project.
