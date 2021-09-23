SERVICES = prometheus_monitor tfl_bikepoint
DASHBOARD = grafana_main
BRIDGE_NET_NAME = user_bridge
PUB_PORT = 3000

all: build run

build: $(addsuffix _build,$(SERVICES)) $(addsuffix _build,$(DASHBOARD)) prune

run: network $(addsuffix _run,$(SERVICES)) $(addsuffix _run_dashboard,$(DASHBOARD))

%_build::
	docker build --rm --file "$*\Dockerfile" --tag $*:latest "$*"

%_run::
	docker run --rm --detach --name $* --network $(BRIDGE_NET_NAME) $*

%_run_dashboard::
	docker run --rm --detach --name $* --network $(BRIDGE_NET_NAME) --publish 3000:$(PUB_PORT) $*

network:
	docker network create $(BRIDGE_NET_NAME)

prune:
	docker image prune -f

stop: $(addsuffix _stop,$(SERVICES)) $(addsuffix _stop,$(DASHBOARD))
	docker network rm $(BRIDGE_NET_NAME)

%_stop::
	-docker container stop $*
