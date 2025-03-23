.PHONY: build
build:
	cargo clippy
	cargo build

.PHONY: release
release:
	cargo build --release

.PHONY: run
run:
	cargo run

.PHONY: test
test:
	cargo test

.PHONY: update
update:
	rustup update

