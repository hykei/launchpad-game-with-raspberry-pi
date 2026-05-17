# Deployment

The project is installed on `hykei-84` at:

```text
~/script/Game
```

## Local Simulator

From the repository root:

```bash
PYTHONPATH=src python3 -m hykei_games --simulator
```

Simulator commands:

- `a3 b4`: move from one square to another
- `reset`: reset current game
- `rotate`: rotate board
- `quit`: exit

## Hardware Install

On `hykei-84`:

```bash
cd ~/script/Game
python3 -m venv --system-site-packages .venv
.venv/bin/python -m pip install -e ".[hardware]"
```

## Run On Hardware

```bash
cd ~/script/Game
.venv/bin/python -u -m hykei_games
```

Current manual background run pattern:

```bash
cd ~/script/Game
setsid .venv/bin/python -u -m hykei_games > game.log 2>&1 < /dev/null &
```

## Verify

```bash
cd ~/script/Game
.venv/bin/python -m unittest discover -s tests -v
```

## Update From Local Development Machine

From the local repository:

```bash
tar --format=ustar -czf /tmp/hykei-games.tgz README.md pyproject.toml src tests docs .gitignore
scp /tmp/hykei-games.tgz hykei-84:~/script/Game/hykei-games.tgz
ssh hykei-84 'cd ~/script/Game && tar -xzf hykei-games.tgz'
```
