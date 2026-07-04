CC ?= gcc
CFLAGS ?= -Wall -Wextra -O2 -fPIC
LDFLAGS ?= -shared -lcrypto

TARGET = libartcb_chain.so
SRC = libartcb_chain.c

.PHONY: all clean test

all: $(TARGET)

$(TARGET): $(SRC) libartcb_chain.h
	$(CC) $(CFLAGS) $(SRC) -o $(TARGET) $(LDFLAGS)

clean:
	rm -f $(TARGET)

test: $(TARGET)
	$(CC) $(CFLAGS) test_chain.c $(SRC) -o test_chain -lcrypto
	./test_chain
