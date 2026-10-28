  const AREAS: Record<string, {name: string; keys: string[]}[]> = {
    "Episode 1": [
      { name: "Forest", keys: ["Booma", "Gobooma", "Gigobooma", "Rag Rappy", "Al Rappy", "Mothmant", "Monest", "Savage Wolf", "Barbarous Wolf", "Hildebear", "Hildeblue", "Dragon",
        "Bartle", "Barble", "Tollaw", "El Rappy", "Pal Rappy", "Mothvert", "Gulgus", "Gulgus-Gue", "Gulgus-gue", "Hildelt", "Hildetorr", "Hidelt", "Hildetor", "Sil Dragon",
        "ブーマ", "ゴブーマ", "ジゴブーマ", "ラグ・ラッピー", "アル・ラッピー", "モスマント", "モネスト", "サベージウルフ", "バーベラスウルフ", "ヒルデベア", "ヒルデブルー", "ドラゴン", "バートル", "バーブル", "トーロウ", "エル・ラッピー", "パル・ラッピー", "モスバートン", "グルグス", "グルグス・グー", "ヒルデルト", "ヒルデトゥール", "ヒデルト", "シル　ドラゴン", "Mothvist"] },
      { name: "Cave", keys: ["Evil Shark", "Pal Shark", "Guil Shark", "Poison Lily", "Nar Lily", "Grass Assassin", "Nano Dragon", "Pofuilly Slime", "Pouilly Slime", "Pan Arms", "Migium", "Hidoom", "De Rol Le",
        "Vulmer", "Govulmer", "GoVulmer", "Melqueek", "Ob Lily", "Mil Lily", "Crimson Assassin", "Pouifully Slime", "Dal Ral Lie",
        "エビルシャーク", "パルシャーク", "ギルシャーク", "ポイゾナスリリー", "ナルリリー", "グラスアサッシン", "ナノノドラゴ", "プフィスライム", "プイィスライム", "パンアームズ", "ミギウム", "ヒドゥーム", "デ・ロル・レ", "バルマー", "ゴバルマ", "メルクィーク", "オブリリー", "ミルリリー", "クリムゾンアサシン", "プイィフリースライム", "ダル・ラ・リー"] },
      { name: "Mine", keys: ["Gilchic", "Dubchic", "Canadine", "Canane", "Sinow Beat", "Sinow Gold", "Garanz", "Vol Opt",
        "Gilchich", "Dubchich", "Gillchich", "Canabin", "Canune", "Sinow Blue", "Sinow Red", "Baranz", "Vol Opt ver.2",
        "ギルチック", "ダブチック", "カナディン", "カナン", "シノワビート", "シノワゴールド", "ギャランゾ", "ボルオプト", "ギルチッチ", "ダブチッチ", "カナバイン", "カヌーン", "シノワブルー", "シノワレッド", "バランゾ", "ボルオプト ver.2", "Gillchic", "Vol Opt ver. 2"] },
      { name: "Ruins", keys: ["Dimenian", "La Dimenian", "So Dimenian", "Delsaber", "Claw", "Bulk", "Bulclaw", "Dark Belra", "Dark Gunner", "Death Gunner", "Chaos Sorcerer", "Chaos Bringer", "Dark Falz",
        "Arlan", "Merlan", "Del-D", "Indi Belra", "Dark Bringer", "Gran Sorcerer",
        "ディメニアン", "ラ・ディメニアン", "ソ・ディメニアン", "デルセイバー", "クロー", "バルク", "バルクロー", "ダークベルラ", "ダークガンナー", "デスガンナー", "カオスソーサラー", "カオスブリンガー", "ダークファルス", "アラン", "メラン", "デルディー", "インディベルラ", "ダークブリンガー", "グランソーサラー"] }
    ],
    "Episode 2": [
      { name: "VR Temple", keys: ["Dimenian", "La Dimenian", "So Dimenian", "Rag Rappy", "Love Rappy", "Egg Rappy", "Halo Rappy", "St. Rappy", "Hildebear", "Hildeblue", "Mothmant", "Monest", "Grass Assassin", "Poison Lily", "Nar Lily", "Dark Belra", "Barba Ray",
        "Arlan", "Merlan", "Del-D", "Mothvert", "El Rappy", "Hidelt", "Hildetor", "Crimson Assassin", "Ob Lily", "Mil Lily", "Indi Belra",
        "ディメニアン", "ラ・ディメニアン", "ソ・ディメニアン", "ラグ・ラッピー", "ラブ・ラッピー", "エグ・ラッピー", "ハロ・ラッピー", "セント・ラッピー", "ヒルデベア", "ヒルデブルー", "モスマント", "モネスト", "グラスアサッシン", "ポイゾナスリリー", "ナルリリー", "ダークベルラ", "バルバレイ", "アラン", "メラン", "デルディー", "モスバートン", "エル・ラッピー", "ヒデルト", "ヒルデトゥール", "クリムゾンアサシン", "オブリリー", "ミルリリー", "インディベルラ", "Mothvist", "Hildelt", "Hildetorr", "Hallo Rappy", "St Rappy"] },
      { name: "VR Spaceship", keys: ["Dubchic", "Gilchic", "Savage Wolf", "Barbarous Wolf", "Pan Arms", "Migium", "Hidoom", "Garanz", "Delsaber", "Chaos Sorcerer", "Gol Dragon",
        "Dubchich", "Gilchich", "Gillchich", "Gulgus", "Gulgus-gue", "Baranz", "Gran Sorcerer",
        "ダブチック", "ギルチック", "サベージウルフ", "バーベラスウルフ", "パンアームズ", "ミギウム", "ヒドゥーム", "ギャランゾ", "デルセイバー", "カオスソーサラー", "ゴル　ドラゴン", "ダブチッチ", "ギルチッチ", "グルグス", "バランゾ", "グランソーサラー", "Gillchic", "ゴルドラゴン"] },
      { name: "Central Control Area", keys: ["Ul Gibbon", "Zol Gibbon", "Merillia", "Meriltas", "Gee", "Sinow Berill", "Sinow Spigell", "Mericarol", "Merikle", "Mericus", "Gibbles", "Gi Gue", "Gal Gryphon",
        "ウル・ギボン", "ゾル・ギボン", "メリルリア", "メリルタス", "ギー", "シノワベリル", "シノワスピゲル", "メリカロル", "メリクル", "メリキュス", "ギブルス", "ギ・グー", "ガル・グリフォン"] },
      { name: "Seabed", keys: ["Dolmolm", "Dolmdarl", "Recon", "Morfos", "Sinow Zoa", "Sinow Zele", "Deldepth", "Delbiter", "Olga Flow",
        "ドルムオルム", "ドルムダール", "レコン", "モルフォス", "シノワゾア", "シノワゼレ", "デルデプス", "デルバイツァ", "オルガ・フロウ"] },
      { name: "Tower", keys: ["Ill Gill", "Del Lily", "Epsilon",
        "イルギル", "デルリリー", "イプシロン"] }
    ],
    "Episode 4": [
      { name: "Crater", keys: ["Boota", "Ze Boota", "Ba Boota", "Astark", "Dorphon", "Dorphon Eclair",
        "ブータ", "ゼ・ブータ", "バ・ブータ", "アスターク", "ドルフォン", "ドルフォン・エクレール"] },
      { name: "Crater / Subterranean Desert", keys: ["Sand Rappy", "Del Rappy", "Satellite Lizard", "Yowie", "Zu", "Pazuzu",
        "サンド・ラッピー", "デル・ラッピー", "サテライト・リザード", "ヨーウィ", "ズー", "パズズ"] },
      { name: "Subterranean Desert", keys: ["Goran", "Pyro Goran", "Goran Detonator", "Merissa A", "Merissa AA", "Girtablulu", "Saint Million", "Shambertin", "Kondrieu",
        "ゴラン", "ピロ・ゴラン", "ゴラン・デトナータ", "メリッサ・エー", "メリッサ・エー・エー", "ギルタブリル", "サンテミリオン", "シャンベルタン", "コンドリュー"] }
    ]
  };

  // episode -> { prekey(lowercased) : areaName }, built lazily.
  const AREA_LOOKUP: Record<string, Record<string, string>> = {};
  export function areaFor(ep: string, englishName: string) {
    var groups = AREAS[ep];
    if (!groups) return null;
    var map = AREA_LOOKUP[ep];
    if (!map) {
      map = AREA_LOOKUP[ep] = {};
      groups.forEach(function (g) {
        g.keys.forEach(function (k) { map[k.toLowerCase()] = g.name; });
      });
    }
    if (!englishName) return null;
    return map[englishName.split('/')[0].trim().replace(/\?$/, '').toLowerCase()] || null;
  }

