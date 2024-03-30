import glob
import hashlib
import os
import platform
import shutil
import subprocess
import time
import zipfile

import fspatch
import img2sdat
import imgextractor
import sdat2img

LOCAL_DIR = os.getcwd()
STEP_TXT = LOCAL_DIR + '/Insides/ONEKEY.CFG'
PLUGIN = LOCAL_DIR + '/Insides/Plugins'
BINS_DIR = LOCAL_DIR + '/Insides/Windows'


def display(message):
    print(f'\x1b[1;33m [ {time.strftime("%H:%M:%S", time.localtime())} ] {message}\x1b[0m')


def cytus_finds(source_dir, end_swith, flag):
    if flag == 1:
        found_files = []
        for parent, _, filenames in os.walk(source_dir, topdown=True):
            for filename in filenames:
                if len(os.path.join(parent, filename).split(os.path.sep)) == len(
                        source_dir.split(os.path.sep)) + 1 and filename.endswith(end_swith):
                    found_files.append(os.path.join(parent, filename))
            return sorted(found_files)
    if flag == 4:
        found_files = []
        for parent, dirnames, filenames in os.walk(source_dir):
            for dirname in dirnames:
                found_files.append(os.path.join(parent, dirname))
            for filename in filenames:
                found_files.append(os.path.join(parent, filename))
        return sorted(found_files)
    elif flag == 5:
        with open(source_dir, 'r') as f:
            return sorted([l.split()[0] for l in f])


def Zarchiver(source, distance, passwd, flag):
    if flag == 1:
        zipfile.ZipFile(source, 'r').extractall(distance)
    if flag == 2:
        with zipfile.ZipFile(source, 'r') as rz:
            rz.extractall(distance, pwd=passwd.encode())
    if flag == 3 and os.path.isdir(source):
        zipout = zipfile.ZipFile(distance, 'w', zipfile.ZIP_DEFLATED)
        os.chdir(source)
        for root, dirs, files in os.walk('.', topdown=False):
            for name in files:
                fullName = os.path.join(root, name)
                zipout.write(fullName)
        os.chdir(LOCAL_DIR)
        zipout.close()
    if flag == 7:
        if passwd != '0':
            os.system(
                BINS_DIR + '/7z x -p' + str(passwd) + ' ' + source + ' -o' + str(distance) + ' -y')
        else:
            os.system(BINS_DIR + '/7z x ' + source + ' -o' + distance + ' -y')


def auto():
    global PROJECT
    os.system('cls')
    display('\x1b[0;32m Unzip \x1b[0;31m' + file + ' \x1b[0m')
    zip_name = os.path.basename(str(file))
    zip_basename = zip_name.split('.zip')[0]
    PROJECT_DIR = 'HNA_' + zip_basename.replace(' ', '_')
    PROJECT = PROJECT_DIR
    Zarchiver(file, PROJECT, 0, 1)
    swith = '.br'
    able_files = cytus_finds(PROJECT, swith, 1)
    for able_file in able_files:
        if os.path.isfile(able_file.rsplit('.', 3)[0] + '.transfer.list'):
            partitionpath = able_file.rsplit('.', 3)[0]
            partition = os.path.splitext(os.path.basename(partitionpath))[0]
            brotlilinux(partition, 1)
            dattoimg(partition)
            display('\x1b[0;32m Extract ' + partition + '.img to folder \x1b[0m')
            imgextractor.Extractor().main(partitionpath + '.img', partitionpath)
            with open(PROJECT + '/000_HNA/partition.txt', 'a') as g:
                g.write(partition + '\n')
    target = os.path.basename(PROJECT + '/system/system')
    props = FindArgs(PROJECT + '/system/system', 'build.prop')
    for prop in props:
        version = cytus_loadglobaldict(prop, 'ro.' + target + '.build.version.incremental')
        device = cytus_loadglobaldict(prop, 'ro.product.' + target + '.device')
        with open(PROJECT + '/000_HNA/romname.txt', 'a') as g:
            g.write(device + '_' + version)
            break
    for SUBS in cytus_loadglobaldict(STEP_TXT, 'RUN_MODULES').split():
        RunModules(PLUGIN + os.sep + SUBS)
    with open(PROJECT + '/000_HNA/partition.txt') as h:
        for partitionname in h:
            partitionname = partitionname.rstrip('\n')
            if os.path.isfile(PROJECT + os.sep + partitionname + '.img'):
                os.system('cls')
                make_ext4fs(partitionname)
                brotlilinux(partitionname, 2)
                shutil.rmtree(PROJECT + os.sep + partitionname)
                os.remove(PROJECT + os.sep + partitionname + '.img')
    with open(PROJECT + '/000_HNA/romname.txt') as j:
        romname = j.readline()[0:-1]
    os.chdir(PROJECT)
    display('\x1b[0;31m Creating zip rom... \x1b[0m')
    os.system(BINS_DIR + '/7z a -tzip {} * -r -mx{} -mmt{} -xr!000_HNA'.format('temp.zip', 0, 5))
    os.chdir(LOCAL_DIR)
    customname = cytus_loadglobaldict(STEP_TXT, 'REPACK_ROMNAME')
    os.rename(PROJECT + '/temp.zip', customname + romname + '_' + md5zip(PROJECT + '/temp.zip') + '.zip')
    if cytus_loadglobaldict(STEP_TXT, 'DELETE_PROJECT_AFTER_DONE') == 'true':
        shutil.rmtree(PROJECT)


def cytus_kernel_img(source, distance, flag=1, orz=' '):
    aik = BINS_DIR + '/kernelkitchen.zip'
    if flag == 1:
        if not os.path.isdir(distance):
            Zarchiver(aik, distance, 0, 1)
            shutil.copytree(source, distance)
            os.system(str(distance) + os.sep + 'unpackimg.bat ' + os.path.basename(source) + ' >/dev/null 2>&1')
            os.remove(str(distance) + os.sep + os.path.basename(source))
            os.remove(str(distance) + os.sep + 'unpackimg.bat')
            os.remove(str(distance) + os.sep + 'repackimg.bat')
            os.remove(str(distance) + os.sep + 'cleanup.bat')
            os.remove(str(distance) + os.sep + 'authors.txt')
            shutil.rmtree(str(distance) + os.sep + 'android_win_tools')
    elif flag == 2 and (not os.path.isfile(distance)):
        siorz = 'original size' if orz == ' --origsize ' else 'minimum size'
        Zarchiver(aik, source, 0, 1)
        sTime = time.time()
        display('\x1b[1;32m Repack: {} <{}> ...\x1b[0m'.format(os.path.basename(distance), siorz))
        os.system(source + os.sep + 'repackimg.bat' + orz + '--forceelf')
        os.remove(source + os.sep + 'unsigned-new.img')
        os.remove(source + os.sep + 'ramdisk-new.cpio.gz')
        os.remove(source + os.sep + 'unpadded-new.img')
        os.remove(source + os.sep + 'unpackimg.bat')
        os.remove(source + os.sep + 'repackimg.bat')
        os.remove(source + os.sep + 'cleanup.bat')
        os.remove(source + os.sep + 'authors.txt')
        shutil.rmtree(source + os.sep + 'android_win_tools')
        if os.path.isfile(source + os.sep + 'image-new.img'):
            os.system('mv ' + source + os.sep + 'image-new.img ' + distance)
            tTime = time.time() - sTime
            display('\x1b[1;32m [%d seconds]\x1b[0m' % tTime)
    else:
        display('\x1b[1;31m [Failed]\x1b[0m')


def make_ext4fs(partition):
    distance = PROJECT + os.sep + partition + '.img'
    source = PROJECT + os.sep + partition
    fsconfig = PROJECT + os.sep + '000_HNA' + os.sep + partition + '_fs_config'
    context = PROJECT + os.sep + '000_HNA' + os.sep + partition + '_file_contexts'
    size = PROJECT + os.sep + '000_HNA' + os.sep + partition + '_size.txt'
    with open(size, 'r') as sz:
        fsize = sz.readline().strip()
    fspatch.main(source, fsconfig)
    if os.path.isfile(distance):
        display('\x1b[0;31m Compressed ' + partition + '.img \x1b[0m')
        os.remove(distance)
        subprocess.run(
            f'{BINS_DIR}/make_ext4fs -s -L {partition} -T -1 -S {context} -C {fsconfig} -l {str(fsize)} -a {partition} {distance} {source}',
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        display('\x1b[0;32m Convert ' + partition + '.img to ' + partition + '.new.dat \x1b[0m')
        img2sdat.main(distance, os.path.dirname(distance), 4, partition)


def brotlilinux(partition, flag):
    brotlicf = cytus_loadglobaldict(STEP_TXT, 'REPACK_BROTLI_LEVEL')
    if flag == 1:
        display('\x1b[0;32m Convert ' + partition + '.new.dat.br to ' + partition + '.new.dat \x1b[0m')
        subprocess.run(BINS_DIR + f"/brotli -dfj {PROJECT + os.sep + partition + '.new.dat.br'}",
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if flag == 2:
        display('\x1b[0;32m Convert ' + partition + '.new.dat to ' + partition + '.new.dat.br \x1b[0m')
        subprocess.run(
            f"{BINS_DIR}/brotli -{brotlicf}jfo {PROJECT + os.sep + partition + '.new.dat.br'} {PROJECT + os.sep + partition + '.new.dat'}",
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def dattoimg(partition):
    display('\x1b[0;32m Convert ' + partition + '.dat to ' + partition + '.img \x1b[0m')
    sdat2img.main(PROJECT + os.sep + partition + '.transfer.list', PROJECT + os.sep + partition + '.new.dat',
                  PROJECT + os.sep + partition + '.img')
    display('\x1b[0;32m Delete original files \x1b[0m')
    os.remove(PROJECT + os.sep + partition + '.transfer.list')
    os.remove(PROJECT + os.sep + partition + '.new.dat')
    os.remove(PROJECT + os.sep + partition + '.patch.dat')


def FindArgs(source_dir, file_name):
    find = []
    for parent, _, filenames in os.walk(source_dir):
        for filename in filenames:
            if file_name == filename:
                find.append(os.path.join(parent, filename))
        return find


def cytus_loadglobaldict(filename, valuename):
    d = []
    f = open(filename)
    for line in f:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if valuename in line:
            d = line.split('=')[-1]
    f.close()
    return d


def menu():
    os.system('cls')
    print(f'\x1b[0;32m\n  PLATFORM : \x1b[0;31m {platform.system()} {platform.release()} \x1b[0m')
    print('\x1b[0;32m  FIRMWARE : \x1b[0;35m' + file + ' \x1b[0m\n')
    print('\x1b[0;37m  --------------------------------------------------\x1b[0m')
    print('\x1b[0;35m  [1] - Auto       [2] - Manual       [Q] - Exit  \x1b[0m\n')
    CHOOSE = input('> Select: ')
    if CHOOSE == '1':
        if file == 'None':
            menu()
        else:
            auto()
    if CHOOSE == '2':
        os.system('cls')
        menu2()
    if CHOOSE == 'Q':
        auto()
    else:
        menu()


def RunModules(sub):
    os.system('cls')
    print('\x1b[1;31m> Plugin running:\x1b[0m ' + os.path.basename(sub) + '\n')
    Shell_Sub = sub + os.sep + 'run.sh'
    if os.path.isfile(Shell_Sub):
        subprocess.run(BINS_DIR + '/busybox sh ' + Shell_Sub + ' ' + PROJECT)
    input()


def md5zip(zipfile):
    with open(zipfile, 'rb') as f:
        file_hash = hashlib.md5()
        while chunk := f.read(8192):
            file_hash.update(chunk)
    return file_hash.hexdigest()[0:10]


def menu2():
    print('\x1b[0;37m  --------------------------------------------------\x1b[0m')
    print('\x1b[0;35m  [22] - Rebuild       [Q] - Exit  \x1b[0m\n')
    CHOOSE = input('> Select: ')
    if CHOOSE == '22':
        PROJECT = LOCAL_DIR + '/HNA_project'
        images = cytus_loadglobaldict(STEP_TXT, 'UNPACK_EXTRA_IMAGES')
        for image in images.split():
            if os.path.exists(PROJECT + os.sep + image):
                display('\x1b[0;32m Unpack ' + image + '\x1b[0m')
                cytus_kernel_img(PROJECT + os.sep + image, PROJECT + os.sep + os.path.splitext(image)[0], 1)
                break
        time.sleep(5)
    if CHOOSE == 'Q':
        print('\x1b[0;32m\n\n  Good bye, see you again!\x1b[0m')
        exit(1)


if __name__ == '__main__':
    # What the Fuck!!!!
    os.chdir(LOCAL_DIR)
    files = glob.glob('*.zip')
    if files:
        for file in files:
            menu()
    else:
        file = 'None'
        menu()
