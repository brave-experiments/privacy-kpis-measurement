import subprocess

import privacykpis.consts
import privacykpis.environment


SYS_KEYCHAIN = "/Library/Keychains/System.keychain"
SUDO_NETWORK_STUB = ["sudo", "networksetup"]


def stdout_of_trusted_shell_cmd(cmd: str) -> str:
    result = subprocess.run(cmd, shell=True, check=True,
                            capture_output=True, text=True)
    return result.stdout.strip()


def get_default_network_service() -> str:
    default_net_piped_cmds = [
        "route -n get default",
        "grep interface",
        r"awk '{print $2}'",
    ]
    default_net_cmd = " | ".join(default_net_piped_cmds)
    default_network_hardware = stdout_of_trusted_shell_cmd(default_net_cmd)

    default_net_service_piped_cmds = [
        "networksetup -listallhardwareports",
        "grep -B 1 {}".format(default_network_hardware),
        "head -n 1",
        r"sed -E 's/.*: (.*)/\1/'"
    ]
    default_net_service_cmd = " | ".join(default_net_service_piped_cmds)
    default_net_service = stdout_of_trusted_shell_cmd(default_net_service_cmd)
    return default_net_service


def setup_env(args: privacykpis.environment.Args) -> None:
    default_net_service = get_default_network_service()
    configure_proxy_cmds = [
        ["-setwebproxy", default_net_service, args.proxy_host,
            args.proxy_port],
        ["-setwebproxystate", default_net_service, "on"],
        ["-setsecurewebproxy", default_net_service, args.proxy_host,
            args.proxy_port],
        ["-setsecurewebproxystate", default_net_service, "on"],
        ["-setproxybypassdomains", default_net_service, "*.apple.com'",
            "*.icloud.com", "*.local", "169.254/16"],
    ]

    sudo_netsetup_stub = ["sudo", "networksetup"]
    for a_cmd in configure_proxy_cmds:
        subprocess.run(SUDO_NETWORK_STUB + a_cmd, check=True)

    trust_cert_cmd = [
        "sudo", "security", "add-trusted-cert", "-d", "-r",
        "trustRoot", "-k", SYS_KEYCHAIN, str(privacykpis.consts.LEAF_CERT)]
    subprocess.run(trust_cert_cmd, check=True)


def teardown_env(args: privacykpis.environment.Args) -> None:
    default_net_service = get_default_network_service()
    configure_proxy_cmds = [
        ["-setwebproxy", default_net_service, "''", "''"],
        ["-setwebproxystate", default_net_service, "off"],
        ["-setsecurewebproxy", default_net_service, "''", "''"],
        ["-setsecurewebproxystate", default_net_service, "off"],
        ["-setproxybypassdomains", default_net_service, "*.local",
            "169.254/16"],
    ]

    for a_cmd in configure_proxy_cmds:
        subprocess.run(SUDO_NETWORK_STUB + a_cmd, check=True)

    untrust_cert_cmd = [
        "sudo", "security", "delete-cert", "-c", "mitmproxy", SYS_KEYCHAIN]
    subprocess.run(untrust_cert_cmd, check=True)
