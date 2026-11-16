# 本地修改：fork 維護用。tw-custom 分支疊在上游 main 之上。
COMPOSE := docker compose -f docker/docker-compose.yml

.PHONY: sync rebuild

# 抓上游 → main 快轉並推到 fork → tw-custom rebase 並推 → 重建容器
sync:
	@test -z "$$(git status --porcelain --untracked-files=no)" || { echo "有未 commit 的改動，先處理"; exit 1; }
	git fetch upstream
	git switch main
	git merge --ff-only upstream/main
	git push origin main
	git switch tw-custom
	git rebase main
	git push --force-with-lease origin tw-custom
	$(MAKE) rebuild

rebuild:
	$(COMPOSE) up -d --build analyzer
