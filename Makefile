CC ?= cc
CFLAGS := -std=c11 -Wall -Wextra -Wpedantic -Werror
SANITIZER_FLAGS := -fsanitize=address,undefined -fno-omit-frame-pointer
BUILD_DIR := build
BUILD_STAMP := $(BUILD_DIR)/.stamp

.PHONY: all build test test-c test-sanitize clean

all: build

build: $(BUILD_DIR)/cfar

$(BUILD_STAMP):
	mkdir -p $(BUILD_DIR)
	touch $(BUILD_STAMP)

$(BUILD_DIR)/cfar: src/main.c src/cfar.c src/cfar.h | $(BUILD_STAMP)
	$(CC) $(CFLAGS) src/main.c src/cfar.c -o $@

$(BUILD_DIR)/test_cfar: tests/test_cfar.c src/cfar.c src/cfar.h | $(BUILD_STAMP)
	$(CC) $(CFLAGS) tests/test_cfar.c src/cfar.c -lm -o $@

$(BUILD_DIR)/test_cfar_sanitize: tests/test_cfar.c src/cfar.c src/cfar.h | $(BUILD_STAMP)
	$(CC) $(CFLAGS) $(SANITIZER_FLAGS) tests/test_cfar.c src/cfar.c -lm -o $@

test: test-c

test-c: $(BUILD_DIR)/test_cfar
	./$(BUILD_DIR)/test_cfar

test-sanitize: $(BUILD_DIR)/test_cfar_sanitize
	./$(BUILD_DIR)/test_cfar_sanitize

clean:
	rm -rf $(BUILD_DIR)
