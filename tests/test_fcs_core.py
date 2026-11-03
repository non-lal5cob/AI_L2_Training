"""Requirement-linked tests for the hardware-independent FCS core."""

import unittest

from fcs import (
    ArmingGate,
    ArmingState,
    Bounds,
    Command,
    FaultPolicy,
    MixerConfig,
    SampleResult,
    SensorRule,
    SensorSample,
    StartupCheck,
    limit_setpoints,
    motor_outputs,
    validate_sample,
    validate_command,
)


class TestFcsCore(unittest.TestCase):
    def test_bounds_reject_invalid_configuration(self):
        with self.assertRaises(ValueError):
            Bounds(2.0, 2.0)
        with self.assertRaises(ValueError):
            Bounds(float("nan"), 2.0)
        with self.assertRaisesRegex(ValueError, "validated bounds"):
            SensorRule({"roll_rate": (-5.0, 5.0)}, max_age_s=0.1)


    def test_sensor_sample_requires_fresh_in_range_complete_data(self):
        rule = SensorRule({"roll_rate": Bounds(-5.0, 5.0)}, max_age_s=0.1)
        self.assertEqual(validate_sample(SensorSample(1.0, {"roll_rate": 0.0}), rule, 1.05), SampleResult(True))
        self.assertEqual(validate_sample(None, rule, 1.05).reason, "missing")
        self.assertEqual(validate_sample(SensorSample(1.0, {"roll_rate": 0.0}), rule, 1.2).reason, "stale")
        self.assertEqual(validate_sample(SensorSample(1.0, {"roll_rate": 6.0}), rule, 1.05).reason, "out_of_range:roll_rate")
        self.assertEqual(validate_sample(SensorSample(1.0, {}), rule, 1.05).reason, "missing:roll_rate")
        self.assertEqual(validate_sample(SensorSample(1.0, {"roll_rate": 0.0}), rule, 1.05, 1.0).reason, "out_of_order")
        self.assertEqual(validate_sample(SensorSample("bad", {"roll_rate": 0.0}), rule, 1.05).reason, "invalid_timestamp")

    def test_ut_006_sf_006_classifies_configured_sensor_samples_with_reasons(self):
        rule = SensorRule({"imu_rate": Bounds(-1.0, 1.0)}, max_age_s=1.0)
        now = 10.0

        valid = validate_sample(SensorSample(10.0, {"imu_rate": 0.0}), rule, now)
        self.assertEqual(valid, SampleResult(True))

        rejected_samples = (
            ("stale", SensorSample(8.0, {"imu_rate": 0.0}), "stale"),
            ("stopped_updates", SensorSample(8.0, {"imu_rate": 0.0}), "stale"),
            ("missing", None, "missing"),
            ("invalid_value", SensorSample(10.0, {"imu_rate": float("nan")}), "invalid:imu_rate"),
            ("out_of_range", SensorSample(10.0, {"imu_rate": 2.0}), "out_of_range:imu_rate"),
        )
        for case, sample, reason in rejected_samples:
            with self.subTest(case=case):
                result = validate_sample(sample, rule, now)
                self.assertEqual(result, SampleResult(False, reason))


    def test_arming_rejects_failed_and_missing_prerequisites_then_disarms(self):
        gate = ArmingGate()
        self.assertFalse(gate.request_arm((StartupCheck("imu", False),), True, True))
        self.assertEqual(gate.inhibit_reasons, ("startup:imu",))
        self.assertFalse(gate.request_arm((), True, True))
        self.assertIn("startup_checks_missing", gate.inhibit_reasons)
        checks = (StartupCheck("imu", True),)
        self.assertTrue(gate.request_arm(checks, True, True))
        self.assertIs(gate.state, ArmingState.ARMED)
        gate.disarm()
        self.assertIs(gate.state, ArmingState.DISARMED)


    def test_fault_policy_selects_highest_priority_and_rejects_unknown_fault(self):
        policy = FaultPolicy(
            priorities={"link_loss": 1, "imu_invalid": 2},
            responses={"link_loss": "configured_link_response", "imu_invalid": "configured_imu_response"},
        )
        self.assertEqual(policy.select(("link_loss", "imu_invalid")), ("imu_invalid", "configured_imu_response"))
        with self.assertRaisesRegex(ValueError, "lack approved policy"):
            policy.select(("unconfigured_fault",))


    def test_setpoints_are_bounded_and_report_limiting(self):
        result = limit_setpoints({"roll": 4.0, "throttle": 0.5}, {"roll": Bounds(-1, 1), "throttle": Bounds(0, 1)})
        self.assertEqual(result.values, (1.0, 0.5))
        self.assertTrue(result.limited)
        with self.assertRaisesRegex(ValueError, "exactly match"):
            limit_setpoints({"roll": 0.0}, {"throttle": Bounds(0, 1)})

    def test_pilot_commands_reject_missing_stale_and_out_of_range_input(self):
        bounds = {"roll": Bounds(-1.0, 1.0), "throttle": Bounds(0.0, 1.0)}
        valid = validate_command(Command(1.0, {"roll": 0.25, "throttle": 0.5}), 1.05, 0.1, bounds)
        self.assertTrue(valid.accepted)
        self.assertEqual(valid.setpoints, (0.25, 0.5))
        self.assertEqual(validate_command(None, 1.05, 0.1, bounds).reason, "missing")
        self.assertEqual(validate_command(Command(1.0, {"roll": 0.0, "throttle": 0.5}), 1.2, 0.1, bounds).reason, "stale")
        self.assertEqual(validate_command(Command("bad", {}), 1.05, 0.1, bounds).reason, "invalid_timestamp")
        invalid = validate_command(Command(1.0, {"roll": 2.0, "throttle": 0.5}), 1.05, 0.1, bounds)
        self.assertEqual(invalid.reason, "out_of_range:roll")


    def test_motors_are_inhibited_disarmed_and_bounded_when_armed(self):
        mixer = MixerConfig(
            matrix=((1.0, 1.0), (1.0, -1.0)),
            output_bounds=Bounds(0.0, 1.0),
            inhibited_value=0.0,
        )
        disarmed = motor_outputs((1.0, 1.0), mixer, ArmingState.DISARMED)
        self.assertEqual(disarmed.values, (0.0, 0.0))
        armed = motor_outputs((0.8, 0.5), mixer, ArmingState.ARMED)
        self.assertEqual(armed.values[0], 1.0)
        self.assertAlmostEqual(armed.values[1], 0.3)
        self.assertTrue(armed.limited)


if __name__ == "__main__":
    unittest.main()