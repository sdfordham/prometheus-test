build_all:
		docker build --rm --file "prometheus_monitor\Dockerfile" --tag prometheus_monitor:latest "prometheus_monitor"
		docker build --rm --file "tfl_bikepoint\Dockerfile" --tag tfl_bikepoint:latest "tfl_bikepoint"
		docker build --rm --file "grafana_main\Dockerfile" --tag grafana_main:latest "grafana_main"
		docker image prune -f

run_all:
		docker network create user_bridge
		docker run --rm --detach --name tfl_bikepoint --network user_bridge tfl_bikepoint
		docker run --rm --detach --name prometheus_monitor --network user_bridge prometheus_monitor
		docker run --rm --detach --name grafana_main --network user_bridge --publish 3000:3000 grafana_main

stop_all:
		docker container stop tfl_bikepoint
		docker container stop prometheus_monitor
		docker container stop grafana_main
		docker network rm user_bridge
