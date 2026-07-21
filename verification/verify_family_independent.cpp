#include <algorithm>
#include <array>
#include <cassert>
#include <cstdlib>
#include <cstdint>
#include <iostream>
#include <queue>
#include <random>
#include <set>
#include <utility>
#include <vector>

#ifdef NDEBUG
#error "verification requires assertions; compile without -DNDEBUG"
#endif

namespace {

using Map = std::vector<int>;

Map compose(const Map& left, const Map& right) {
  Map result(right.size());
  for (std::size_t index = 0; index < right.size(); ++index) {
    result[index] = left[right[index]];
  }
  return result;
}

std::vector<int> profile(const Map& map) {
  std::vector<int> counts(map.size());
  for (int target : map) ++counts[target];
  counts.erase(std::remove(counts.begin(), counts.end(), 0), counts.end());
  std::sort(counts.begin(), counts.end());
  return counts;
}

int rank(const Map& map) {
  return static_cast<int>(profile(map).size());
}

std::pair<Map, Map> construct(int m) {
  const int path_size = 2 * m + 1;
  const int state_count = 2 * path_size;
  Map coloring(state_count);
  Map shift(state_count);
  for (int index = 0; index < path_size; ++index) {
    coloring[index] = index % 2;
    coloring[path_size + index] = index % 2;
    shift[index] = path_size + index;
    shift[path_size + index] = index + 1 < path_size ? index + 1 : index - 1;
  }
  return {coloring, shift};
}

bool is_path_endomorphism(const Map& map, int m) {
  const int path_size = 2 * m + 1;
  auto adjacent = [path_size](int left, int right) {
    const bool same_side = (left < path_size) == (right < path_size);
    return same_side && std::abs((left % path_size) - (right % path_size)) == 1;
  };
  for (int side : {0, path_size}) {
    for (int index = 0; index + 1 < path_size; ++index) {
      if (!adjacent(map[side + index], map[side + index + 1])) return false;
    }
  }
  return true;
}

bool strongly_connected(const std::array<Map, 2>& generators) {
  const int size = static_cast<int>(generators[0].size());
  for (int source = 0; source < size; ++source) {
    std::vector<bool> reached(size);
    std::queue<int> frontier;
    reached[source] = true;
    frontier.push(source);
    while (!frontier.empty()) {
      const int current = frontier.front();
      frontier.pop();
      for (const Map& generator : generators) {
        const int target = generator[current];
        if (reached[target]) continue;
        reached[target] = true;
        frontier.push(target);
      }
    }
    if (!std::all_of(reached.begin(), reached.end(), [](bool value) { return value; })) {
      return false;
    }
  }
  return true;
}

std::vector<Map> closure(const std::array<Map, 2>& generators) {
  Map identity(generators[0].size());
  for (std::size_t index = 0; index < identity.size(); ++index) identity[index] = index;
  std::vector<Map> elements{identity};
  std::set<Map> seen{identity};
  for (std::size_t cursor = 0; cursor < elements.size(); ++cursor) {
    for (const Map& generator : generators) {
      Map candidate = compose(generator, elements[cursor]);
      if (seen.insert(candidate).second) elements.push_back(std::move(candidate));
    }
  }
  return elements;
}

void verify(int m, std::mt19937_64& random) {
  auto [coloring, shift] = construct(m);
  const std::array<Map, 2> generators{coloring, shift};
  assert(is_path_endomorphism(coloring, m));
  assert(is_path_endomorphism(shift, m));
  assert(strongly_connected(generators));
  assert(coloring[0] == 0);

  const std::vector<int> unbalanced{2 * m, 2 * m + 2};
  const std::vector<int> balanced{2 * m + 1, 2 * m + 1};
  Map power(coloring.size());
  for (std::size_t index = 0; index < power.size(); ++index) power[index] = index;
  for (int time = 0; time < 8 * m + 17; ++time) {
    Map collapsed = compose(coloring, power);
    assert(profile(collapsed) == (time % 2 == 0 ? unbalanced : balanced));
    const std::vector<int> locked = profile(collapsed);
    for (int step = 0; step < 100; ++step) {
      collapsed = compose(generators[random() & 1U], collapsed);
      assert(rank(collapsed) == 2);
      assert(profile(collapsed) == locked);
    }
    power = compose(shift, power);
  }

  const std::vector<Map> semigroup = closure(generators);
  assert(semigroup.size() == static_cast<std::size_t>(20 * m + 2));
  int minimum_rank = static_cast<int>(coloring.size());
  std::set<std::vector<int>> minimum_profiles;
  for (const Map& map : semigroup) minimum_rank = std::min(minimum_rank, rank(map));
  for (const Map& map : semigroup) {
    if (rank(map) == minimum_rank) minimum_profiles.insert(profile(map));
  }
  assert(minimum_rank == 2);
  assert(minimum_profiles == std::set<std::vector<int>>({unbalanced, balanced}));
  std::cout << "m=" << m << " states=" << coloring.size()
            << " semigroup=" << semigroup.size() << " PASS\n";
}

}  // namespace

int main() {
  std::mt19937_64 random(0xC0A1E5CEULL);
  for (int m = 1; m <= 24; ++m) verify(m, random);
  std::cout << "independent C++ family verification: PASS\n";
}
