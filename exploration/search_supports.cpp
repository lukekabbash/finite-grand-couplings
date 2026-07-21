#include <algorithm>
#include <array>
#include <cstdint>
#include <iostream>
#include <queue>
#include <set>
#include <tuple>
#include <vector>

using Map = std::array<std::uint8_t, 4>;

int main() {
  std::array<Map, 256> maps{};
  std::array<std::uint8_t, 256> rank{};
  std::array<std::uint8_t, 256> profile{}; // 13, 22, or 0
  for (int code = 0; code < 256; ++code) {
    int x = code;
    std::array<int, 4> counts{};
    for (int i = 0; i < 4; ++i) {
      maps[code][i] = x % 4;
      ++counts[maps[code][i]];
      x /= 4;
    }
    for (int c : counts) rank[code] += (c != 0);
    std::sort(counts.begin(), counts.end());
    if (counts == std::array<int, 4>{0, 0, 1, 3}) profile[code] = 13;
    if (counts == std::array<int, 4>{0, 0, 2, 2}) profile[code] = 22;
  }

  std::array<std::array<std::uint8_t, 256>, 256> compose{};
  for (int a = 0; a < 256; ++a) {
    for (int b = 0; b < 256; ++b) {
      int code = 0;
      int place = 1;
      for (int i = 0; i < 4; ++i) {
        code += place * maps[a][maps[b][i]]; // a o b
        place *= 4;
      }
      compose[a][b] = static_cast<std::uint8_t>(code);
    }
  }

  auto strongly_connected = [&](const std::array<int, 3>& gens, int count) {
    for (int source = 0; source < 4; ++source) {
      std::array<bool, 4> seen{};
      std::queue<int> todo;
      seen[source] = true;
      todo.push(source);
      while (!todo.empty()) {
        int u = todo.front(); todo.pop();
        for (int gidx = 0; gidx < count; ++gidx) {
          int v = maps[gens[gidx]][u];
          if (!seen[v]) { seen[v] = true; todo.push(v); }
        }
      }
      if (!std::all_of(seen.begin(), seen.end(), [](bool x) { return x; })) return false;
    }
    return true;
  };

  auto close = [&](const std::array<int, 3>& gens, int count,
                   std::array<bool, 256>& present,
                   bool& has13, bool& has22) {
    present.fill(false);
    std::vector<int> elements;
    for (int j = 0; j < count; ++j) {
      if (!present[gens[j]]) {
        present[gens[j]] = true;
        elements.push_back(gens[j]);
      }
    }
    for (size_t cursor = 0; cursor < elements.size(); ++cursor) {
      int a = elements[cursor];
      if (rank[a] == 1) return false;
      if (profile[a] == 13) has13 = true;
      if (profile[a] == 22) has22 = true;
      // Multiplication against every element known at loop entry; newly added
      // elements get their own cursor, so both directions are eventually seen.
      size_t known = elements.size();
      for (size_t j = 0; j < known; ++j) {
        int b = elements[j];
        for (int c : {int(compose[a][b]), int(compose[b][a])}) {
          if (rank[c] == 1) return false;
          if (!present[c]) { present[c] = true; elements.push_back(c); }
        }
      }
    }
    return true;
  };

  std::array<bool, 256> present{};
  std::uint64_t sc2 = 0, sc3 = 0, no_constant3 = 0;
  std::array<int, 3> gens{};
  for (int a = 0; a < 256; ++a) {
    for (int b = a + 1; b < 256; ++b) {
      gens = {a, b, 0};
      if (strongly_connected(gens, 2)) {
        ++sc2;
        bool p13 = false, p22 = false;
        if (close(gens, 2, present, p13, p22) && p13 && p22) {
          std::cout << "HIT support=2 codes " << a << ' ' << b << '\n';
          return 1;
        }
      }
      for (int c = b + 1; c < 256; ++c) {
        gens = {a, b, c};
        if (!strongly_connected(gens, 3)) continue;
        ++sc3;
        bool p13 = false, p22 = false;
        if (!close(gens, 3, present, p13, p22)) continue;
        ++no_constant3;
        if (p13 && p22) {
          std::cout << "HIT support=3 codes " << a << ' ' << b << ' ' << c << '\n';
          for (int code : gens) {
            std::cout << '(';
            for (int i = 0; i < 4; ++i) std::cout << int(maps[code][i]) << (i == 3 ? ')' : ',');
            std::cout << '\n';
          }
          return 1;
        }
      }
    }
  }
  std::cout << "NO_HIT support<=3\n";
  std::cout << "strongly_connected_pairs=" << sc2 << '\n';
  std::cout << "strongly_connected_triples=" << sc3 << '\n';
  std::cout << "rank_at_least_two_triples=" << no_constant3 << '\n';
}
