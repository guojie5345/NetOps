[{
            "enable": 0,
            "src_zone": {
                "name": "Any"
            },
            "src_addr": {
                "member": "testadd1",
                "type": "0"
            },
            "src_subnet": {
                "ip": "26.3.3.3",
                "netmask": "24"
            },
            "src_range": {
                "min": "25.6.6.6",
                "max": "25.6.6.16"
            },
            "src_host": {
                "host": "test",
                "is_ipv6": "0"
            },
            "dst_zone": {
                "name": "Any"
            },
            "dst_addr": {
                "member": "testadd2",
                "type": "0"
            },
            "service": [{
                "member": "BFD"
            }, {
                "member": "AIM"
            }
            ],
            "service_row": [{
                "protocol": "6",
                "dst_port_low": "2",
                "dst_port_high": "2",
                "src_port_low": "3",
                "src_port_high": "3"
            }, {
                "protocol": "17",
                "dst_port_low": "11",
                "dst_port_high": "12",
                "src_port_low": "11",
                "src_port_high": "13"
            }],
            "icmp": [{
                "icmpname": 3,
                "code_min": "4",
                "code_max": "4"
            }],
            "icmpv6": [{
                "icmpname": 1,
                "code_min": "25",
                "code_max": "25"
            }],
            "protocol": [{
                "protocol": 112
            }],
            "application": {
                "member": "apptest1"
            },
            "idp": {
                "name": "predef_default"
            },
            "av": {
                "name": "predef_middle"
            },
            "action": "1",
            "log_deny": "1",
            "log_end": "1",
            "log_start": "1",
            "assistant_enable": "0",
            "schedname": {
                "name": "sched1"
            }
        }]