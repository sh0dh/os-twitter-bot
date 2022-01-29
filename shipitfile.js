module.exports = shipit => {
    // Load shipit-deploy tasks
    require('shipit-deploy')(shipit)
    require('shipit-shared')(shipit)
    require('shipit-submodule')(shipit);

    var currentPath = "./";
    var deployUserPath = "/home/deploy/vandul-bot/current"

    shipit.initConfig({
        default: {
            workspace: currentPath,
            deployTo: "/home/deploy/vandul-bot",
            repositoryUrl: "git@github.com:pratos/vandul-twitter-bot-rq.git",
            ignores: [".git", "node_modules", "tests", ".pre-commit-config.yaml"],
            keepRelease: 2,
            keepWorkspace: false,
            deleteOnRollback: true,
            key: "/Users/prthamesh/.ssh/streetmelt_pratos",
            asUser: "deploy",
            verboseSSHLevel: 0
        },
        prod: {
            branch: "main",
            servers: "root@164.90.246.53",
        }
    })

    shipit.blTask('docker:run-test', async () => {
        shipit.log('Install asdf');
        await shipit.remote(`docker run hello-world`)
    });

    shipit.blTask('server:setup', async () => {
        shipit.log('Build docker images');
        await shipit.remote(`cd ${deployUserPath} && pip --version && python3 --version && pip install poetry==1.1.8`)
        await shipit.remote(`cd ${deployUserPath} && source $HOME/.poetry/env && poetry env use 3.8.10 && poetry install`)
        await shipit.remote(`cd ${deployUserPath} && source $HOME/.poetry/env && mkdir -p db && poetry run db:migrate`)
        await shipit.remote(`cd ${deployUserPath} && sudo cp systemd/streetmelt.service /etc/systemd/system/streetmelt.service`)
        await shipit.remote(`cd ${deployUserPath} && sudo cp systemd/kanz.service /etc/systemd/system/kanz.service`)
        await shipit.remote(`sudo systemctl daemon-reload`)
        await shipit.remote(`sudo systemctl enable streetmelt.service && sudo systemctl start streetmelt.service`)
        await shipit.remote(`sudo systemctl enable kanz.service && sudo systemctl start kanz.service`)
        await shipit.remote(`sudo systemctl status streetmelt.service`)
        await shipit.remote(`sudo systemctl status kanz.service`)
    });

    shipit.on('published', () => {
        shipit.start('server:setup');
    })
}