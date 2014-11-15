from setuptools import setup

setup(
        name='ssh_manage_api',
        version='1.0',
        description='simple batch manage ssh_keys and support web api',
        author='fengyun.rui',
        author_email='rfyiamcool@163.com',
        url='https://github.com/rfyiamcool',
        packages=['ssh_manage_api'],
        install_requires=['sh'],
        license='BSD',
        platforms='mac \ linux',
        classifiers=[
                'Operating System :: Unix',
                'Programming Language :: Python :: 2',
                'Programming Language :: Python :: 2.7',
                'Programming Language :: Python :: 3',
                'Programming Language :: Python :: 3.3',
        ],
)
