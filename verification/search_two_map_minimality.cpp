#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <queue>
#include <vector>

namespace {

template <int N>
struct Search {
  static constexpr int map_count = [] {
    int value = 1;
    for (int i = 0; i < N; ++i) value *= N;
    return value;
  }();

  using Map = std::array<std::uint8_t, N>;

  std::array<Map, map_count> maps{};
  std::array<std::uint8_t, map_count> ranks{};
  std::array<std::uint32_t, map_count> profiles{};
  std::vector<std::uint16_t> composition;
  std::array<std::uint32_t, map_count> seen{};
  std::uint32_t stamp = 0;

  Search() : composition(static_cast<std::size_t>(map_count) * map_count) {
    for (int code = 0; code < map_count; ++code) {
      int value = code;
      std::array<std::uint8_t, N> counts{};
      for (int i = 0; i < N; ++i) {
        maps[code][i] = static_cast<std::uint8_t>(value % N);
        ++counts[maps[code][i]];
        value /= N;
      }
      std::sort(counts.begin(), counts.end());
      std::uint32_t profile = 0;
      for (std::uint8_t count : counts) {
        if (count == 0) continue;
        ++ranks[code];
        profile = (profile << 3U) | count;
      }
      profiles[code] = profile;
    }

    for (int left = 0; left < map_count; ++left) {
      for (int right = 0; right < map_count; ++right) {
        int code = 0;
        int place = 1;
        for (int i = 0; i < N; ++i) {
          code += place * maps[left][maps[right][i]];
          place *= N;
        }
        composition[static_cast<std::size_t>(left) * map_count + right] =
            static_cast<std::uint16_t>(code);
      }
    }
  }

  std::uint16_t compose(int left, int right) const {
    return composition[static_cast<std::size_t>(left) * map_count + right];
  }

  bool strongly_connected(int first, int second) const {
    for (int source = 0; source < N; ++source) {
      std::array<bool, N> reached{};
      std::queue<int> frontier;
      reached[source] = true;
      frontier.push(source);
      while (!frontier.empty()) {
        const int current = frontier.front();
        frontier.pop();
        for (int generator : {first, second}) {
          const int next = maps[generator][current];
          if (reached[next]) continue;
          reached[next] = true;
          frontier.push(next);
        }
      }
      if (!std::all_of(reached.begin(), reached.end(), [](bool value) { return value; })) {
        return false;
      }
    }
    return true;
  }

  bool has_random_profile(int first, int second, std::size_t& closure_size,
                          int& minimum_rank) {
    ++stamp;
    const int identity = [] {
      int code = 0;
      int place = 1;
      for (int i = 0; i < N; ++i) {
        code += i * place;
        place *= N;
      }
      return code;
    }();

    std::vector<std::uint16_t> elements{static_cast<std::uint16_t>(identity)};
    seen[identity] = stamp;
    bool synchronized = false;
    for (std::size_t cursor = 0; cursor < elements.size() && !synchronized; ++cursor) {
      for (int generator : {first, second}) {
        const std::uint16_t next = compose(generator, elements[cursor]);
        if (ranks[next] == 1) {
          synchronized = true;
          break;
        }
        if (seen[next] == stamp) continue;
        seen[next] = stamp;
        elements.push_back(next);
      }
    }

    closure_size = elements.size();
    if (synchronized) {
      minimum_rank = 1;
      return false;
    }

    minimum_rank = N;
    for (std::uint16_t element : elements) {
      minimum_rank = std::min(minimum_rank, static_cast<int>(ranks[element]));
    }

    std::uint32_t first_profile = 0;
    for (std::uint16_t element : elements) {
      if (ranks[element] != minimum_rank) continue;
      if (first_profile == 0) {
        first_profile = profiles[element];
      } else if (profiles[element] != first_profile) {
        return true;
      }
    }
    return false;
  }

  int run() {
    std::uint64_t pairs = 0;
    std::uint64_t strongly_connected_pairs = 0;
    std::uint64_t nonsynchronizing_pairs = 0;
    for (int first = 0; first < map_count; ++first) {
      for (int second = first + 1; second < map_count; ++second) {
        ++pairs;
        if (!strongly_connected(first, second)) continue;
        ++strongly_connected_pairs;
        std::size_t closure_size = 0;
        int minimum_rank = 0;
        if (has_random_profile(first, second, closure_size, minimum_rank)) {
          std::cout << "HIT n=" << N << " maps=" << first << ',' << second
                    << " closure=" << closure_size << " min_rank=" << minimum_rank << '\n';
          for (int code : {first, second}) {
            std::cout << '(';
            for (int i = 0; i < N; ++i) {
              std::cout << static_cast<int>(maps[code][i]) << (i + 1 == N ? ')' : ',');
            }
            std::cout << '\n';
          }
          return 1;
        }
        if (minimum_rank > 1) ++nonsynchronizing_pairs;
      }
    }
    std::cout << "NO_HIT n=" << N << '\n';
    std::cout << "pairs=" << pairs << '\n';
    std::cout << "strongly_connected_pairs=" << strongly_connected_pairs << '\n';
    std::cout << "nonsynchronizing_pairs=" << nonsynchronizing_pairs << '\n';

    std::uint64_t expected_pairs = 0;
    std::uint64_t expected_strongly_connected = 0;
    std::uint64_t expected_nonsynchronizing = 0;
    if constexpr (N == 4) {
      expected_pairs = 32'640;
      expected_strongly_connected = 10'476;
      expected_nonsynchronizing = 1'152;
    } else if constexpr (N == 5) {
      expected_pairs = 4'881'250;
      expected_strongly_connected = 1'277'160;
      expected_nonsynchronizing = 60'000;
    }
    if (pairs != expected_pairs ||
        strongly_connected_pairs != expected_strongly_connected ||
        nonsynchronizing_pairs != expected_nonsynchronizing) {
      std::cerr << "ERROR: exhaustive-search counts differ from the frozen reference\n";
      return 2;
    }
    return 0;
  }
};

}  // namespace

int main() {
#if STATE_COUNT == 4
  return Search<4>().run();
#elif STATE_COUNT == 5
  return Search<5>().run();
#else
#error "Compile with -DSTATE_COUNT=4 or -DSTATE_COUNT=5"
#endif
}
