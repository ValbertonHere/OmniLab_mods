import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react-swc'

// Пути к играм.
// mt_ruby = '/home/valberton/Games/Tanki/res_mods/1.40.0.0/gui/gameface/mods/'
// wot_eu = 'C:/Program Files (x86)/SteamLibrary/steamapps/common/World of Tanks/ru/res_mods/2.0.1.1/gui/gameface/mods'
// my_git_folder = '/home/valberton/HDD/HDD1/CodeWORK/JavaScript/mto_gameface/valberton/mto_legacy_lobby_header/build/'

const cgf_mods_folder = './valberton/user_customization_test/build/'

// Название папки в репозитории и название мода (HTML-файла).
const mod_folder = 'valberton/user_customization_test/'
const mod_file = 'UserCustomizationTestView'

function virtualExternal(spec = 'virtual:model', target = '../../libs/model.js') {
    return {
        name: 'virtual-external-model',
        enforce: "pre",
        resolveId(source: string) {
        if (source === spec) {
            // Keep the exact specifier in the bundle and mark it external
            return {id: target, external: true};
        }
        return null;
        },
    };
}

export default defineConfig({
    plugins: [react(), 
              virtualExternal('gameface:common', '../../libs/common.js'),
              virtualExternal('gameface:debug', '../../libs/debug.js'),
              virtualExternal('gameface:media', '../../libs/media.js'),
              virtualExternal('gameface:model', '../../libs/model.js'),
              virtualExternal('gameface:sound', '../../libs/sound.js'),
              virtualExternal('gameface:views', '../../libs/views.js')],
    base: './',
    root: mod_folder,
    build: {
        outDir: cgf_mods_folder + mod_folder,
        emptyOutDir: true,
        rollupOptions: {
            input: {
                main: mod_folder + mod_file + '.html',
            },
            output: {
                entryFileNames: mod_file + '.js',
                assetFileNames: mod_file + '.css',
            }
        }
    }
})