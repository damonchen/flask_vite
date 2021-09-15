from os import path as _path
import json
from urllib.parse import urljoin
from flask import current_app, _app_ctx_stack, Markup

class Vite(object):

  def __init__(self, app=None):
    self.app = app
    self._manifest = None
    if self.app is not None:
      self.init_app(app)

  def init_app(self, app):
    app.config.setdefault('VITE_DEV_MODE', False)
    app.config.setdefault('VITE_DEV_SERVER_PROTOCOL', 'http')
    app.config.setdefault('VITE_DEV_SERVER_HOST', 'localhost')
    app.config.setdefault('VITE_DEV_SERVER_PORT', '3000')
    app.config.setdefault('VITE_WS_CLIENT_URL', '@vite/client')
    app.config.setdefault('VITE_STATIC_ROOT', self.static_root)
    app.config.setdefault('VITE_STATIC_URL', self.static_url)

    vite_assets_path = app.config.get('VITE_ASSETS_PATH')

    debug = app.config.get('DEBUG')
    static_root = app.config.get('VITE_STATIC_ROOT')
    default_vite_manifest_path = _path.join(vite_assets_path if debug else static_root, 'manifest.json')
    app.config.setdefault('VITE_MANIFEST_PATH', default_vite_manifest_path)

    if not app.config['VITE_DEV_MODE']:
      self._parse_manifest()

    @app.context_processor
    def context_processor():
      return dict(
        vite_url_for=self.vite_url_for,
        vite_asset_url=self.vite_asset_url,
        vite_asset=self.vite_asset,
        vite_hmr_client=self.vite_hmr_client,
      )

    app.teardown_appcontext(self.teardown)

  def teardown(self, exception):
    # using for clear
    ctx = _app_ctx_stack.top
    if hasattr(ctx, 'xxx'):
      pass

  def _parse_manifest(self):
    vite_manifest_path = self.app.config['VITE_MANIFEST_PATH']
    try:
      with open(vite_manifest_path, 'r') as fp:
        manifest_content = fp.read()
      self._manifest = json.loads(manifest_content)
    except Exception as error:
      raise RuntimeError(
        f"Cannot read Vite manifest file at "
        f"{vite_manifest_path} : {str(error)}"
      )

  @property
  def static_root(self):
    return _path.join(self.app.root_path, self.app.static_folder)

  @property
  def static_url(self):
    return self.app.static_url_path

  def _generate_vite_server_url(self, path):
    vite_dev_server_protocol = self.app.config.get('VITE_DEV_SERVER_PROTOCOL')
    vite_dev_server_host = self.app.config.get('VITE_DEV_SERVER_HOST')
    vite_dev_server_port = self.app.config.get('VITE_DEV_SERVER_PORT')
    static_url = self.app.config.get('VITE_STATIC_URL')
    path = path.lstrip('/')

    return urljoin(
      f'{vite_dev_server_protocol}://'
      f'{vite_dev_server_host}:{vite_dev_server_port}',
      _path.join(static_url, path if path is not None else '')
    )

  def _generate_script_tag(self, src, attrs):
    if attrs is not None:
      attrs_str = ' '.join([f'{key}="{value}"' for key, value in attrs.items()])
    else:
      attrs_str = ''

    return f'<script {attrs_str} src="{src}"> </script>'

  def _generate_stylesheet_tag(self, href):
    return f'<link rel="stylesheet" href="{href}" />'

  def generate_vite_ws_client(self):
    if not self.app.config['VITE_DEV_MODE']:
      return ""

    ws_client_url = self._generate_vite_server_url(self.app.config['VITE_WS_CLIENT_URL'])
    return self._generate_script_tag(ws_client_url, {'type': 'module'})

  def generate_vite_asset(self, path, script_attrs, with_imports):
    if self.app.config['VITE_DEV_MODE']:
      return self._generate_script_tag(self._generate_vite_server_url(path),
        {'type': 'module', 'async': '', 'defer': ''})

    if path not in self._manifest:
      vite_manifest_path = self.app.config['VITE_MANIFEST_PATH']
      raise RuntimeError(
        f'Cannot find {path} in Vite manifest '
        f'at {vite_manifest_path}'
      )
    script_attrs = script_attrs or {'type': 'module', 'async': '', 'defer': ''}
    tags = []
    manifest_entry = self._manifest.get(path)

    static_url = self.app.config['VITE_STATIC_URL']

    if 'css' in manifest_entry:
      for css_path in manifest_entry['css']:
        tags.append(
          self._generate_stylesheet_tag(
            urljoin(static_url, css_path),
          )
        )

    if with_imports and 'imports' in manifest_entry:
      for vendor_path in manifest_entry['imports']:
        tags.append(
          self.generate_vite_asset(
            vendor_path,
            script_attrs=script_attrs,
            with_imports=with_imports,
          )
        )

    tags.append(
      self._generate_script_tag(
        urljoin(static_url, manifest_entry['file']),
        attrs=script_attrs,
      )
    )

    return '\n'.join(tags)


  def generate_vite_asset_url(self, path):
    if self.app.config.get('VITE_DEV_MODE'):
      self._generate_vite_server_url(path)

    if path not in self._manifest:
      return RuntimeError(
        f'Cannot find {path} in Vite manifest '
        f'at {self.app.config["VITE_MANIFEST_PATH"]}'
      )

    return urljoin(self.static_url, self._manifest[path]['file'])

  def vite_url_for(self, path, **kwargs):
    if self.app.config['VITE_DEV_MODE']:
      return self._generate_vite_server_url(path)

    if path not in self._manifest:
      raise RuntimeError(
        f'Cannot find {path} in Vite manifest '
        f'at {self.app.config["VITE_MANIFEST_PATH"]}'
      )

    return urljoin(self.static_url, self._manifest[path]['file'])

  def vite_asset_url(self, path):
    assert path is not None
    return Markup(self.generate_vite_asset_url(path))

  def vite_asset(self, path, script_attrs=None, with_imports=True):
    assert path is not None
    return Markup(self.generate_vite_asset(path, script_attrs=script_attrs, with_imports=with_imports))

  def vite_hmr_client(self):
    return Markup(self.generate_vite_ws_client())
