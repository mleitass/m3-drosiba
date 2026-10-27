# Ezermalas e-pakalpojums "Iesniegumi" · drošības pārbaude. Saraksts: make help
SHELL := /bin/bash
PY ?= python
VEIDNE ?= https://github.com/mleitass/m3-drosiba.git
export PYTHONIOENCODING := utf-8

.DEFAULT_GOAL := help
.PHONY: help parbaude sagatavot paraugs katalogs run test

help: ## Parāda komandas
	@awk -F ':.*## ' '/^[a-zA-Z_%-]+:.*## / {printf "  make %-12s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

parbaude: ## Pirms nodarbības: vai Codespace ir gatavs
	@PY="$(PY)" VEIDNE="$(VEIDNE)" bash riki/parbaude.sh

sagatavot: ## Nodarbības sākumā: sagatavo jūsu kopiju (vienreiz)
	@VEIDNE="$(VEIDNE)" bash riki/sagatavot.sh

paraugs: ## Parauga atskaite mapē paraugs/ (tikai pēc savas skenēšanas)
	@git fetch -q --no-tags "$(VEIDNE)" paraugs \
	  && git show FETCH_HEAD:paraugs/CLAUDE-SECURITY-RESULTS.md > paraugs/CLAUDE-SECURITY-RESULTS.md \
	  && echo "Atveriet paraugs/CLAUDE-SECURITY-RESULTS.md"

katalogs: ## "Savs skeneris": IKT resursu katalogs pret PHP2Shell brīdinājumu
	@$(PY) riki/katalogs.py dati/katalogs.csv || true

run: ## Palaiž API (ports 8000, dokumentācija /docs)
	$(PY) -m uvicorn app.main:app --host 0.0.0.0 --port 8000

test: ## Palaiž testus
	@$(PY) -m pytest -q
