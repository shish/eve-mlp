# vim:ft=python
a = Analysis(['main_gui.py'])
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas + [
        ("icon.ico", "icon.ico", "DATA"),
        ("help.html", "help.html", "DATA"),
        ("LICENSE.txt", "LICENSE.txt", "DATA"),
    ],
    name=os.path.join('dist', 'eve-gmlp'),
    debug=False,
    strip=None,
    upx=True,
    console=True,
    icon='icon.ico'
)
app = BUNDLE(
    exe,
    name=os.path.join('dist', 'eve-gmlp.app')
)


a = Analysis(['main_cli.py'])
pyz = PYZ(a.pure)
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    name=os.path.join('dist', 'eve-mlp'),
    debug=False,
    strip=None,
    upx=True,
    console=True,
    icon='icon.ico'
)
