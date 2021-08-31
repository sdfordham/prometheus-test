build_all:
		docker build --rm -f "prometheus_monitor\Dockerfile" -t prometheus_monitor:latest "prometheus_monitor"
		docker build --rm -f "tfl_bikepoint\Dockerfile" -t tfl_bikepoint:latest "tfl_bikepoint"
		docker image prune -f

run_all:
		docker network create user_bridge
		docker run --rm --detach --name tfl_bikepoint --network user_bridge tfl_bikepoint
		docker run --rm --detach --name prometheus_monitor --network user_bridge --publish 9090:9090 prometheus_monitor

stop_all:
		docker container stop tfl_bikepoint
		docker container stop prometheus_monitor
		docker network rm user_bridge
