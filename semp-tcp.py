#!/usr/bin/env python3

import argparse
import configparser
import importlib
import logging
import sys
import threading
import time
import traceback

from pymodbus.server import StartTcpServer
from pymodbus.constants import Endian
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSlaveContext
from pymodbus.datastore import ModbusServerContext
from pymodbus.payload import BinaryPayloadBuilder

# Protocol for WattNode register list: https://ctlsys.com/wp-content/uploads/2016/10/WNC-Modbus-Register-List-V18.xls
def t_update(ctx, stop, module, device, refresh):

    this_t = threading.current_thread()
    logger = logging.getLogger()

    while not stop.is_set():
        try:
            values = module.values(device)

            if not values:
                logger.debug(f"{this_t.name}: no new values")
                continue
            
            block_1001 = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            block_1001.add_32bit_float(values.get("energy_active", 0)) # total active energy
            block_1001.add_32bit_float(values.get("import_energy_active", 0)) # imported active energy
            block_1001.add_32bit_float(values.get("energy_active", 0)) # total active energy non-reset
            block_1001.add_32bit_float(values.get("import_energy_active", 0)) # imported active energy non-reset
            block_1001.add_32bit_float(values.get("power_active", 0)) # total power
            block_1001.add_32bit_float(values.get("l1_power_active", 0)) # power l1
            block_1001.add_32bit_float(values.get("l2_power_active", 0)) # power l2
            block_1001.add_32bit_float(values.get("l3_power_active", 0)) # power l3
            block_1001.add_32bit_float(values.get("voltage_ln", 0)) # l-n voltage
            block_1001.add_32bit_float(values.get("l1n_voltage", 0)) # l1-n voltage
            block_1001.add_32bit_float(values.get("l2n_voltage", 0)) # l2-n voltage
            block_1001.add_32bit_float(values.get("l3n_voltage", 0)) # l3-n voltage
            block_1001.add_32bit_float(values.get("voltage_ll", 0)) # l-l voltage
            block_1001.add_32bit_float(values.get("l12_voltage", 0)) # l1-l2 voltage
            block_1001.add_32bit_float(values.get("l23_voltage", 0)) # l2-l3 voltage
            block_1001.add_32bit_float(values.get("l31_voltage", 0)) # l3-l1 voltage
            block_1001.add_32bit_float(values.get("frequency", 0)) # line frequency
            ctx.setValues(3, 1000, block_1001.to_registers())

            block_1101 = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
            block_1101.add_32bit_float(values.get("l1_energy_active", 0)) # total active energy l1
            block_1101.add_32bit_float(values.get("l2_energy_active", 0)) # total active energy l2
            block_1101.add_32bit_float(values.get("l3_energy_active", 0)) # total active energy l3
            block_1101.add_32bit_float(values.get("l1_import_energy_active", 0)) # imported active energy l1
            block_1101.add_32bit_float(values.get("l2_import_energy_active", 0)) # imported active energy l2
            block_1101.add_32bit_float(values.get("l3_import_energy_active", 0)) # imported active energy l3
            block_1101.add_32bit_float(values.get("export_energy_active", 0)) # total exported active energy
            block_1101.add_32bit_float(values.get("export_energy_active", 0)) # total exported active energy non-reset
            block_1101.add_32bit_float(values.get("l1_export_energy_active", 0)) # exported energy l1
            block_1101.add_32bit_float(values.get("l2_export_energy_active", 0)) # exported energy l2
            block_1101.add_32bit_float(values.get("l3_export_energy_active", 0)) # exported energy l3
            block_1101.add_32bit_float(values.get("energy_reactive", 0)) # total reactive energy
            block_1101.add_32bit_float(values.get("l1_energy_reactive", 0)) # reactive energy l1
            block_1101.add_32bit_float(values.get("l2_energy_reactive", 0)) # reactive energy l2
            block_1101.add_32bit_float(values.get("l3_energy_reactive", 0)) # reactive energy l3
            block_1101.add_32bit_float(values.get("energy_apparent", 0)) # total apparent energy
            block_1101.add_32bit_float(values.get("l1_energy_apparent", 0)) # apparent energy l1
            block_1101.add_32bit_float(values.get("l2_energy_apparent", 0)) # apparent energy l2
            block_1101.add_32bit_float(values.get("l3_energy_apparent", 0)) # apparent energy l3
            block_1101.add_32bit_float(values.get("power_factor", 0)) # power factor
            block_1101.add_32bit_float(values.get("l1_power_factor", 0)) # power factor l1
            block_1101.add_32bit_float(values.get("l2_power_factor", 0)) # power factor l2
            block_1101.add_32bit_float(values.get("l3_power_factor", 0)) # power factor l3
            block_1101.add_32bit_float(values.get("power_reactive", 0)) # total reactive power
            block_1101.add_32bit_float(values.get("l1_power_reactive", 0)) # reactive power l1
            block_1101.add_32bit_float(values.get("l2_power_reactive", 0)) # reactive power l2
            block_1101.add_32bit_float(values.get("l3_power_reactive", 0)) # reactive power l3
            block_1101.add_32bit_float(values.get("power_apparent", 0)) # total apparent power
            block_1101.add_32bit_float(values.get("l1_power_apparent", 0)) # apparent power l1
            block_1101.add_32bit_float(values.get("l2_power_apparent", 0)) # apparent power l2
            block_1101.add_32bit_float(values.get("l3_power_apparent", 0)) # apparent power l3
            block_1101.add_32bit_float(values.get("l1_current", 0)) # current l1
            block_1101.add_32bit_float(values.get("l2_current", 0)) # current l2
            block_1101.add_32bit_float(values.get("l3_current", 0)) # current l3
            block_1101.add_32bit_float(values.get("demand_power_active", 0)) # demand power
            block_1101.add_32bit_float(values.get("minimum_demand_power_active", 0)) # minimum demand power
            block_1101.add_32bit_float(values.get("maximum_demand_power_active", 0)) # maximum demand power
            block_1101.add_32bit_float(values.get("demand_power_apparent", 0)) # apparent demand power
            block_1101.add_32bit_float(values.get("l1_demand_power_active", 0)) # demand power l1
            block_1101.add_32bit_float(values.get("l2_demand_power_active", 0)) # demand power l2
            block_1101.add_32bit_float(values.get("l3_demand_power_active", 0)) # demand power l3
            ctx.setValues(3, 1100, block_1101.to_registers())
        except Exception as e:
            logger.critical(f"{this_t.name}: {e}")
            print(traceback.format_exc())
        finally:
            time.sleep(refresh)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-c", "--config", type=str, default="semp-tcp.conf")
    argparser.add_argument("-v", "--verbose", action="store_true", default=False)
    args = argparser.parse_args()

    default_config = {
        "server": {
            "address": "0.0.0.0",
            "port": 5502,
            "framer": "socket",
            "log_level": "INFO",
            "meters": ''
        },
        "meters": {
            "dst_address": 2,
            "type": "generic",
            "ct_current": 5,
            "ct_inverted": 0,
            "phase_offset": 120,
            "serial_number": 987654,
            "refresh_rate": 5
        }
    }

    confparser = configparser.ConfigParser()
    confparser.read(args.config)

    if not confparser.has_section("server"):
        confparser["server"] = default_config["server"]

    log_handler = logging.StreamHandler(sys.stdout)
    log_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))

    logger = logging.getLogger()
    logger.setLevel(getattr(logging, confparser["server"].get("log_level", fallback=default_config["server"]["log_level"]).upper()))
    logger.addHandler(log_handler)

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    slaves = {}
    threads = []
    thread_stops = []

    try:
        if confparser.has_option("server", "meters"):
            meters = [m.strip() for m in confparser["server"].get("meters", fallback=default_config["server"]["meters"]).split(',')]

            for meter in meters:
                address = confparser[meter].getint("dst_address", fallback=default_config["meters"]["dst_address"])
                meter_type = confparser[meter].get("type", fallback=default_config["meters"]["type"])
                meter_module = importlib.import_module(f"devices.{meter_type}")
                meter_device = meter_module.device(confparser[meter])

                slave_ctx = ModbusSlaveContext()

                block_1601 = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
                block_1601.add_32bit_int(1234) # config passcode
                block_1601.add_16bit_int(confparser[meter].getint("ct_current", fallback=default_config["meters"]["ct_current"])) # ct rated current
                block_1601.add_16bit_int(confparser[meter].getint("ct_current", fallback=default_config["meters"]["ct_current"])) # ct rated current l1
                block_1601.add_16bit_int(confparser[meter].getint("ct_current", fallback=default_config["meters"]["ct_current"])) # ct rated current l2
                block_1601.add_16bit_int(confparser[meter].getint("ct_current", fallback=default_config["meters"]["ct_current"])) # ct rated current l3
                block_1601.add_16bit_int(confparser[meter].getint("ct_inverted", fallback=default_config["meters"]["ct_inverted"])) # ct direction inversion
                block_1601.add_16bit_int(0) # measurement averaging
                block_1601.add_16bit_int(0) # power scale
                block_1601.add_16bit_int(15) # demand period
                block_1601.add_16bit_int(1) # demand subintervals
                block_1601.add_16bit_int(10000) # power/energy adjustment l1
                block_1601.add_16bit_int(10000) # power/energy adjustment l2
                block_1601.add_16bit_int(10000) # power/energy adjustment l3
                block_1601.add_16bit_int(-1000) # ct phase angle adjustment l1
                block_1601.add_16bit_int(-1000) # ct phase angle adjustment l2
                block_1601.add_16bit_int(-1000) # ct phase angle adjustment l3
                block_1601.add_16bit_int(1500) # minimum power reading
                block_1601.add_16bit_int(confparser[meter].getint("phase_offset", fallback=default_config["meters"]["phase_offset"])) # phase offset
                block_1601.add_16bit_int(0) # reset energy
                block_1601.add_16bit_int(0) # reset demand
                block_1601.add_16bit_int(20000) # current scale
                block_1601.add_16bit_int(0) # io pin mode
                slave_ctx.setValues(3, 1600, block_1601.to_registers())

                block_1651 = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
                block_1651.add_16bit_int(0) # apply config
                block_1651.add_16bit_int(address) # modbus address
                block_1651.add_16bit_int(4) # baud rate
                block_1651.add_16bit_int(0) # parity mode
                block_1651.add_16bit_int(0) # modbus mode
                block_1651.add_16bit_int(5) # message delay
                slave_ctx.setValues(3, 1650, block_1651.to_registers())

                block_1701 = BinaryPayloadBuilder(byteorder=Endian.BIG, wordorder=Endian.LITTLE)
                block_1701.add_32bit_int(confparser[meter].getint("serial_number", fallback=default_config["meters"]["serial_number"])) # serial number
                block_1701.add_32bit_int(0) # uptime (s)
                block_1701.add_32bit_int(0) # total uptime (s)
                block_1701.add_16bit_int(202) # wattnode model
                block_1701.add_16bit_int(31) # firmware version
                block_1701.add_16bit_int(0) # wattnode options
                block_1701.add_16bit_int(0) # error status
                block_1701.add_16bit_int(0) # power fail count
                block_1701.add_16bit_int(0) # crc error count
                block_1701.add_16bit_int(0) # frame error count
                block_1701.add_16bit_int(0) # packet error count
                block_1701.add_16bit_int(0) # overrun count
                block_1701.add_16bit_int(0) # error status 1
                block_1701.add_16bit_int(0) # error status 2
                block_1701.add_16bit_int(0) # error status 3
                block_1701.add_16bit_int(0) # error status 4
                block_1701.add_16bit_int(0) # error status 5
                block_1701.add_16bit_int(0) # error status 6
                block_1701.add_16bit_int(0) # error status 7
                block_1701.add_16bit_int(0) # error status 8
                slave_ctx.setValues(3, 1700, block_1701.to_registers())

                update_t_stop = threading.Event()
                update_t = threading.Thread(
                    target=t_update,
                    name=f"t_update_{address}",
                    args=(
                        slave_ctx,
                        update_t_stop,
                        meter_module,
                        meter_device,
                        confparser[meter].getint("refresh_rate", fallback=default_config["meters"]["refresh_rate"])
                    )
                )

                threads.append(update_t)
                thread_stops.append(update_t_stop)

                slaves.update({address: slave_ctx})
                logger.info(f"Created {update_t}: {meter} {meter_type} {meter_device}")

        if not slaves:
            logger.warning(f"No meters defined in {args.config}")

        config_framer = confparser["server"].get("framer", fallback=default_config["server"]["framer"])
        framer = False

        if config_framer == "socket":
            framer = "socket"
        elif config_framer == "rtu":
            framer = "rtu"

        identity = ModbusDeviceIdentification()
        server_ctx = ModbusServerContext(slaves=slaves, single=False)

        time.sleep(1)

        for t in threads:
            t.start()
            logger.info(f"Starting {t}")

        server = StartTcpServer(
            context=server_ctx,
            framer=framer,
            identity=identity,
            address=(
                confparser["server"].get("address", fallback=default_config["server"]["address"]),
                confparser["server"].getint("port", fallback=default_config["server"]["port"])
            )
        )
    except KeyboardInterrupt:
        pass
    finally:
        for t_stop in thread_stops:
            t_stop.set()
        for t in threads:
            t.join()
