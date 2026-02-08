# Makefile for UCIS C API implementation

CC = gcc
CFLAGS = -Wall -Wextra -O2 -fPIC -I. -DSQLITE_ENABLE_COLUMN_METADATA
LDFLAGS = -shared -lpthread -ldl -lm

SOURCES = sqlite3.c ucis_api.c ucis_handle.c ucis_util.c ucis_schema.c \
          ucis_scope.c ucis_iterator.c ucis_cover.c
OBJECTS = $(SOURCES:.c=.o)
TARGET = libucis.so

.PHONY: all clean test fetch-sqlite

all: fetch-sqlite $(TARGET)

fetch-sqlite:
	@bash fetch_sqlite3.sh

$(TARGET): $(OBJECTS)
	$(CC) $(LDFLAGS) -o $@ $^

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@

clean:
	rm -f $(OBJECTS) $(TARGET) *.ucisdb

test: $(TARGET)
	@echo "Running tests..."
	@cd test && python3 test_basic.py

.PHONY: install
install: $(TARGET)
	install -D $(TARGET) $(DESTDIR)/usr/lib/$(TARGET)
	install -D ucis.h $(DESTDIR)/usr/include/ucis.h
	install -D ucis_types.h $(DESTDIR)/usr/include/ucis_types.h
