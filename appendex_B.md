# 付録B pacman.c 全関数索引

pacman.c の関数定義の一覧です。行番号は
コミット `ccfc0e84` のものです。

| 行 | 関数 | 区画 |
|---|---|---|
| 716 | `sokol_main` | APPLICATION ENTRY AND CALLBACKS |
| 732 | `init` | APPLICATION ENTRY AND CALLBACKS |
| 744 | `frame` | APPLICATION ENTRY AND CALLBACKS |
| 782 | `input` | APPLICATION ENTRY AND CALLBACKS |
| 819 | `cleanup` | APPLICATION ENTRY AND CALLBACKS |
| 827 | `xorshift32` | GRAB BAG OF HELPER FUNCTIONS |
| 835 | `levelspec` | GRAB BAG OF HELPER FUNCTIONS |
| 844 | `start` | GRAB BAG OF HELPER FUNCTIONS |
| 849 | `start_after` | GRAB BAG OF HELPER FUNCTIONS |
| 854 | `disable` | GRAB BAG OF HELPER FUNCTIONS |
| 859 | `disabled_timer` | GRAB BAG OF HELPER FUNCTIONS |
| 864 | `now` | GRAB BAG OF HELPER FUNCTIONS |
| 869 | `since` | GRAB BAG OF HELPER FUNCTIONS |
| 879 | `between` | GRAB BAG OF HELPER FUNCTIONS |
| 891 | `after_once` | GRAB BAG OF HELPER FUNCTIONS |
| 896 | `after` | GRAB BAG OF HELPER FUNCTIONS |
| 907 | `before` | GRAB BAG OF HELPER FUNCTIONS |
| 918 | `input_disable` | GRAB BAG OF HELPER FUNCTIONS |
| 923 | `input_enable` | GRAB BAG OF HELPER FUNCTIONS |
| 928 | `input_dir` | GRAB BAG OF HELPER FUNCTIONS |
| 947 | `i2` | GRAB BAG OF HELPER FUNCTIONS |
| 952 | `add_i2` | GRAB BAG OF HELPER FUNCTIONS |
| 957 | `sub_i2` | GRAB BAG OF HELPER FUNCTIONS |
| 962 | `mul_i2` | GRAB BAG OF HELPER FUNCTIONS |
| 967 | `squared_distance_i2` | GRAB BAG OF HELPER FUNCTIONS |
| 973 | `equal_i2` | GRAB BAG OF HELPER FUNCTIONS |
| 978 | `nearequal_i2` | GRAB BAG OF HELPER FUNCTIONS |
| 983 | `actor_to_sprite_pos` | GRAB BAG OF HELPER FUNCTIONS |
| 988 | `dist_to_tile_mid` | GRAB BAG OF HELPER FUNCTIONS |
| 993 | `vid_clear` | GRAB BAG OF HELPER FUNCTIONS |
| 999 | `vid_color_playfield` | GRAB BAG OF HELPER FUNCTIONS |
| 1008 | `valid_tile_pos` | GRAB BAG OF HELPER FUNCTIONS |
| 1013 | `vid_color` | GRAB BAG OF HELPER FUNCTIONS |
| 1019 | `vid_tile` | GRAB BAG OF HELPER FUNCTIONS |
| 1025 | `vid_color_tile` | GRAB BAG OF HELPER FUNCTIONS |
| 1032 | `conv_char` | GRAB BAG OF HELPER FUNCTIONS |
| 1045 | `vid_color_char` | GRAB BAG OF HELPER FUNCTIONS |
| 1052 | `vid_char` | GRAB BAG OF HELPER FUNCTIONS |
| 1058 | `vid_color_text` | GRAB BAG OF HELPER FUNCTIONS |
| 1073 | `vid_text` | GRAB BAG OF HELPER FUNCTIONS |
| 1092 | `vid_color_score` | GRAB BAG OF HELPER FUNCTIONS |
| 1115 | `vid_draw_tile_quad` | GRAB BAG OF HELPER FUNCTIONS |
| 1125 | `vid_fruit_score` | GRAB BAG OF HELPER FUNCTIONS |
| 1134 | `spr_clear` | GRAB BAG OF HELPER FUNCTIONS |
| 1139 | `spr_pacman` | GRAB BAG OF HELPER FUNCTIONS |
| 1144 | `spr_ghost` | GRAB BAG OF HELPER FUNCTIONS |
| 1150 | `spr_fruit` | GRAB BAG OF HELPER FUNCTIONS |
| 1155 | `spr_anim_pacman` | GRAB BAG OF HELPER FUNCTIONS |
| 1170 | `spr_anim_pacman_death` | GRAB BAG OF HELPER FUNCTIONS |
| 1182 | `spr_anim_ghost` | GRAB BAG OF HELPER FUNCTIONS |
| 1199 | `spr_anim_ghost_frightened` | GRAB BAG OF HELPER FUNCTIONS |
| 1219 | `spr_anim_ghost_eyes` | GRAB BAG OF HELPER FUNCTIONS |
| 1230 | `pixel_to_tile_pos` | GRAB BAG OF HELPER FUNCTIONS |
| 1235 | `clamped_tile_pos` | GRAB BAG OF HELPER FUNCTIONS |
| 1253 | `dir_to_vec` | GRAB BAG OF HELPER FUNCTIONS |
| 1260 | `reverse_dir` | GRAB BAG OF HELPER FUNCTIONS |
| 1270 | `tile_code_at` | GRAB BAG OF HELPER FUNCTIONS |
| 1277 | `is_blocking_tile` | GRAB BAG OF HELPER FUNCTIONS |
| 1282 | `is_dot` | GRAB BAG OF HELPER FUNCTIONS |
| 1287 | `is_pill` | GRAB BAG OF HELPER FUNCTIONS |
| 1292 | `is_tunnel` | GRAB BAG OF HELPER FUNCTIONS |
| 1298 | `is_redzone` | GRAB BAG OF HELPER FUNCTIONS |
| 1304 | `can_move` | GRAB BAG OF HELPER FUNCTIONS |
| 1334 | `move` | GRAB BAG OF HELPER FUNCTIONS |
| 1363 | `dbg_marker` | GRAB BAG OF HELPER FUNCTIONS |
| 1377 | `game_init_playfield` | GAMEPLAY CODE |
| 1434 | `game_disable_timers` | GAMEPLAY CODE |
| 1447 | `game_init` | GAMEPLAY CODE |
| 1467 | `game_round_init` | GAMEPLAY CODE |
| 1584 | `game_update_tiles` | GAMEPLAY CODE |
| 1639 | `game_update_sprites` | GAMEPLAY CODE |
| 1733 | `game_pacman_should_move` | GAMEPLAY CODE |
| 1750 | `game_ghost_speed` | GAMEPLAY CODE |
| 1777 | `game_scatter_chase_phase` | GAMEPLAY CODE |
| 1792 | `game_update_ghost_state` | GAMEPLAY CODE |
| 1886 | `game_update_ghost_target` | GAMEPLAY CODE |
| 1957 | `game_update_ghost_dir` | GAMEPLAY CODE |
| 2067 | `game_update_ghosthouse_dot_counters` | GAMEPLAY CODE |
| 2089 | `game_update_dots_eaten` | GAMEPLAY CODE |
| 2111 | `game_update_actors` | GAMEPLAY CODE |
| 2217 | `game_tick` | GAMEPLAY CODE |
| 2326 | `intro_tick` | INTRO GAMESTATE CODE |
| 2404 | `gfx_create_resources` | GFX SUBSYSTEM |
| 2820 | `gfx_decode_tile` | GFX SUBSYSTEM |
| 2829 | `gfx_decode_sprite` | GFX SUBSYSTEM |
| 2847 | `gfx_decode_tiles` | GFX SUBSYSTEM |
| 2867 | `gfx_decode_color_palette` | GFX SUBSYSTEM |
| 2893 | `gfx_init` | GFX SUBSYSTEM |
| 2913 | `gfx_shutdown` | GFX SUBSYSTEM |
| 2917 | `gfx_add_vertex` | GFX SUBSYSTEM |
| 2927 | `gfx_add_tile_vertices` | GFX SUBSYSTEM |
| 2958 | `gfx_add_playfield_vertices` | GFX SUBSYSTEM |
| 2968 | `gfx_add_debugmarker_vertices` | GFX SUBSYSTEM |
| 2977 | `gfx_add_sprite_vertices` | GFX SUBSYSTEM |
| 3017 | `gfx_add_fade_vertices` | GFX SUBSYSTEM |
| 3036 | `gfx_adjust_viewport` | GFX SUBSYSTEM |
| 3052 | `gfx_fade` | GFX SUBSYSTEM |
| 3069 | `gfx_draw` | GFX SUBSYSTEM |
| 3125 | `snd_init` | AUDIO SUBSYSTEM |
| 3140 | `snd_shutdown` | AUDIO SUBSYSTEM |
| 3145 | `snd_voice_tick` | AUDIO SUBSYSTEM |
| 3160 | `snd_sample_tick` | AUDIO SUBSYSTEM |
| 3177 | `snd_frame` | AUDIO SUBSYSTEM |
| 3196 | `snd_tick` | AUDIO SUBSYSTEM |
| 3232 | `snd_clear` | AUDIO SUBSYSTEM |
| 3238 | `snd_start` | AUDIO SUBSYSTEM |
| 3266 | `snd_stop` | AUDIO SUBSYSTEM |
| 3281 | `snd_func_eatdot1` | AUDIO SUBSYSTEM |
| 3298 | `snd_func_eatdot2` | AUDIO SUBSYSTEM |
| 3315 | `snd_func_eatghost` | AUDIO SUBSYSTEM |
| 3332 | `snd_func_eatfruit` | AUDIO SUBSYSTEM |
| 3352 | `snd_func_weeooh` | AUDIO SUBSYSTEM |
| 3369 | `snd_func_frightened` | AUDIO SUBSYSTEM |
