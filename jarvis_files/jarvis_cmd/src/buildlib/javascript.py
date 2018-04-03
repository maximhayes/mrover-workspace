import os

from jarvis.core import shell, ln, rm, ensure_dir

from . import Builder


class YarnBuilder(Builder):
    def is_relevant_file(self, name):
        return (os.path.splitext(name)[1] in (
                    '.js', '.html', '.json', '.lock') or
                os.path.basename(os.path.dirname(name)) == 'static')

    def _build(self, intermediate):
        app = self.params.get('app', False)
        if app:
            shell('yarn')
            dep_root = os.path.join(intermediate, 'deps')
            if not os.path.exists(dep_root):
                ensure_dir(dep_root)

            for dep in self.dep_names:
                dep_mod_dir = os.path.join(
                        self.wksp.product_env, 'share', 'js', dep)
                dep_dir = os.path.join(
                        intermediate, 'deps', dep)
                rm(dep_dir)
                ln(dep_mod_dir, dep_dir)
            shell('yarn run build')

        # copy things into product env
        dist_dir = os.path.join(self.wksp.product_env,
                                'share', 'js', self.name)
        ensure_dir(dist_dir)
        ln(os.path.join(intermediate, 'dist'),
           os.path.join(dist_dir, 'dist'))
        if os.path.exists(os.path.join(intermediate, 'package.json')):
            ln(os.path.join(intermediate, 'package.json'),
               os.path.join(dist_dir, 'package.json'))
        if os.path.exists(os.path.join(intermediate, 'yarn.lock')):
            ln(os.path.join(intermediate, 'yarn.lock'),
               os.path.join(dist_dir, 'yarn.lock'))

        if app:
            script_path = os.path.join(self.wksp.product_env, 'bin', self.name)
            self.wksp.template(
                    'webapp_start',
                    script_path,
                    app_dir=dist_dir,
                    port=self.params.get('port', 8010))
            os.chmod(script_path, 0o755)
