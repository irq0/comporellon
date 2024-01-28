// Tool to display images on a Waveshare 7.5" e-ink display.
// Compile: g++ -o display-waveshare -lpng -llgpio -lm display.cc
// Requires png++, libpng, lg (https://abyz.me.uk/lg/)

#include <algorithm>
#include <array>
#include <iostream>
#include <lgpio.h>
#include <png++/gray_pixel.hpp>
#include <png++/png.hpp>
#include <vector>

constexpr int PIN_RST = 17;
constexpr int PIN_DATA_COMMAND = 25;
constexpr int PIN_CHIP_SELECT = 8;
constexpr int PIN_PWR = 18;
constexpr int PIN_BUSY = 24;

constexpr int WIDTH = 800;
constexpr int HEIGHT = 480;

enum Commands {
  SET_COLOR = 0x10,
  SET_COLOR_INVERSE = 0x13,
};

static void display_wait_idle(int gpio) {
  std::cout << "busy. waiting for idle" << std::endl;
  do {
    lguSleep(0.020);
  } while (lgGpioRead(gpio, PIN_BUSY) >= 1);
  lguSleep(0.020);
  std::cout << "idle" << std::endl;
}

static void display_reset(int gpio) {
  lgGpioWrite(gpio, PIN_RST, 1);
  lguSleep(0.020);
  lgGpioWrite(gpio, PIN_RST, 0);
  lguSleep(0.002);
  lgGpioWrite(gpio, PIN_RST, 1);
  lguSleep(0.020);
}

template <class It>
static void display_command(int gpio, int spi, uint8_t command, It first,
                            It last) {
  lgGpioWrite(gpio, PIN_DATA_COMMAND, 0);
  lgGpioWrite(gpio, PIN_CHIP_SELECT, 0);
  lgSpiWrite(spi, reinterpret_cast<char *>(&command), 1);
  lgGpioWrite(gpio, PIN_CHIP_SELECT, 1);

  lgGpioWrite(gpio, PIN_DATA_COMMAND, 1);
  lgGpioWrite(gpio, PIN_CHIP_SELECT, 0);
  std::for_each(first, last, [&](uint8_t byte) {
    lgSpiWrite(spi, reinterpret_cast<char *>(&byte), 1);
  });
  lgGpioWrite(gpio, PIN_CHIP_SELECT, 1);
}

static void display_command(int gpio, int spi, uint8_t command,
                            std::initializer_list<uint8_t> args) {
  display_command(gpio, spi, command, std::begin(args), std::end(args));
}

static void display_command(int gpio, int spi, uint8_t command) {
  display_command(gpio, spi, command, {});
}

static void display_sleep(int gpio, int spi) {
  // Power Off
  display_command(gpio, spi, 0x02);
  display_wait_idle(gpio);
  // Deep Sleep
  display_command(gpio, spi, 0x07, {0xA5});
}

static void display_refresh(int gpio, int spi) {
  display_command(gpio, spi, 0x12);
  lguSleep(0.100);
  display_wait_idle(gpio);
}

static void display_clear(int gpio, int spi, bool color) {
  const int pixels = WIDTH * HEIGHT / 8;
  const char color_byte = color ? 0xFF : 0x00;

  {
    const char command = Commands::SET_COLOR;
    lgGpioWrite(gpio, PIN_DATA_COMMAND, 0);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 0);
    lgSpiWrite(spi, &command, 1);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 1);
    lgGpioWrite(gpio, PIN_DATA_COMMAND, 1);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 0);
    for (int i = 0; i < pixels; ++i) {
      lgSpiWrite(spi, &color_byte, 1);
    }
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 1);
  }

  {
    const char command = Commands::SET_COLOR_INVERSE;
    lgGpioWrite(gpio, PIN_DATA_COMMAND, 0);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 0);
    lgSpiWrite(spi, &command, 1);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 1);
    lgGpioWrite(gpio, PIN_DATA_COMMAND, 1);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 0);
    const char inverse_color_byte = ~color_byte;
    for (int i = 0; i < pixels; ++i) {
      lgSpiWrite(spi, &inverse_color_byte, 1);
    }
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 1);
  }
}

static void display_image(int gpio, int spi, const std::string &filename) {
  png::image<png::gray_pixel_1> image(
      filename, png::require_color_space<png::gray_pixel_1>());
  if (image.get_width() != WIDTH || image.get_height() != HEIGHT) {
    std::cerr << "Image size must be " << WIDTH << "x" << HEIGHT << std::endl;
    return;
  }

  // Note: display expects bytes, where each represents 8 pixels
  {
    const char command = Commands::SET_COLOR;
    lgGpioWrite(gpio, PIN_DATA_COMMAND, 0);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 0);
    lgSpiWrite(spi, &command, 1);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 1);
    lgGpioWrite(gpio, PIN_DATA_COMMAND, 1);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 0);
    for (int x = 0; x < image.get_height(); x++) {
      lgSpiWrite(spi, reinterpret_cast<char *>(image.get_row(x).get_data()),
                 image.get_width() / 8);
    }
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 1);
  }
  {
    const char command = Commands::SET_COLOR_INVERSE;
    lgGpioWrite(gpio, PIN_DATA_COMMAND, 0);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 0);
    lgSpiWrite(spi, &command, 1);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 1);
    lgGpioWrite(gpio, PIN_DATA_COMMAND, 1);
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 0);
    for (int x = 0; x < image.get_height(); x++) {
      std::array<char, WIDTH / 8> row_inverse;
      std::transform(image.get_row(x).get_data(),
                     image.get_row(x).get_data() + WIDTH / 8,
                     row_inverse.begin(), [](char c) { return ~c; });
      lgSpiWrite(spi, row_inverse.data(), image.get_width() / 8);
    }
    lgGpioWrite(gpio, PIN_CHIP_SELECT, 1);
  }
}

static void display_init(int gpio, int spi) {
  // general init
  lgGpioClaimInput(gpio, 0, PIN_BUSY);
  lgGpioClaimOutput(gpio, 0, PIN_RST, LG_LOW);
  lgGpioClaimOutput(gpio, 0, PIN_DATA_COMMAND, LG_LOW);
  lgGpioClaimOutput(gpio, 0, PIN_CHIP_SELECT, LG_LOW);
  lgGpioClaimOutput(gpio, 0, PIN_PWR, LG_LOW);

  lgGpioWrite(gpio, PIN_CHIP_SELECT, 1);
  lgGpioWrite(gpio, PIN_PWR, 1);

  // 7.5 inch display init
  display_reset(gpio);
  // Power Setting
  display_command(gpio, spi, 0x01, {0x07, 0x07, 0x3f, 0x3f});
  // Booster Soft Start
  display_command(gpio, spi, 0x06, {0x17, 0x17, 0x28, 0x17});
  // Power On
  display_command(gpio, spi, 0x04);
  // Wait till on
  lguSleep(0.100);
  display_wait_idle(gpio);
  // Panel Setting
  display_command(gpio, spi, 0x00, {0x1f});
  // Resolution Setting
  display_command(gpio, spi, 0x61, {0x03, 0x20, 0x01, 0xe0});
  // Dual SPI
  display_command(gpio, spi, 0x15, {0x00});
  // VCOM and Data Interval Setting
  display_command(gpio, spi, 0x50, {0x10, 0x07});
  // TCON Setting
  display_command(gpio, spi, 0x60, {0x22});
}

static void display_shutdown(int gpio, int spi) {
  lgGpioWrite(gpio, PIN_CHIP_SELECT, 0);
  lgGpioWrite(gpio, PIN_PWR, 0);
  lgGpioWrite(gpio, PIN_DATA_COMMAND, 0);
  lgGpioWrite(gpio, PIN_RST, 0);
}

int main(int argc, char **argv) {
  const auto gpio = lgGpiochipOpen(0);
  if (gpio < 0) {
    std::cerr << "Failed to open gpiochip 0" << std::endl;
    return 1;
  }
  const auto spi = lgSpiOpen(0, 0, 10000000, 0);
  if (spi < 0) {
    std::cerr << "Failed to open SPI0.0" << std::endl;
    return 1;
  }
  std::cout << "display init" << std::endl;
  display_init(gpio, spi);
  std::cout << "display image" << std::endl;
  display_image(gpio, spi, argv[1]);
  std::cout << "refresh" << std::endl;
  display_refresh(gpio, spi);
  std::cout << "shutdown" << std::endl;
  lguSleep(5.0);

  display_sleep(gpio, spi);
  display_shutdown(gpio, spi);
  lgSpiClose(spi);
  lgGpiochipClose(gpio);
}
