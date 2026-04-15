import base64
import json
import os
from copy import deepcopy
from datetime import datetime

from google.protobuf.json_format import MessageToDict
from loguru import logger
from liqi_new import decode as liqi_decode
from proto import liqi_pb2 as pb
from ruamel.yaml import YAML


class round_recorder:
    START_METHODS = {
        ".lq.NotifyRoomGameStart",
        ".lq.NotifyMatchGameStart",
        ".lq.NotifyNewGame",
    }
    END_METHODS = {
        ".lq.NotifyGameEndResult",
        ".lq.NotifyGameTerminate",
        ".lq.NotifyGameFinishReward",
        ".lq.NotifyGameFinishRewardV2",
    }
    PAIPU_METHOD = ".lq.Lobby.fetchGameRecord"

    def __init__(self):
        self.yaml = YAML()
        self._load_settings()
        self.output_dir = self.settings["config"]["output_dir"]
        self.pretty = self.settings["config"]["pretty"]
        os.makedirs(self.output_dir, exist_ok=True)

        self.current_game = None
        logger.success(f"已载入round_recorder，输出目录：{self.output_dir}")

    def _load_settings(self):
        self.settings = self.yaml.load(
            """\
config:
  output_dir: './recordings'  # 对局数据输出目录
  pretty: true  # 是否格式化输出json
"""
        )
        try:
            with open("./config/settings.recorder.yaml", "r", encoding="utf-8") as f:
                self.settings.update(self.yaml.load(f))
        except Exception:
            logger.warning(
                "未检测到recorder配置文件，已生成默认配置，如需自定义请手动修改 ./config/settings.recorder.yaml"
            )
            self._save_settings()

    def _save_settings(self):
        with open("./config/settings.recorder.yaml", "w", encoding="utf-8") as f:
            self.yaml.dump(self.settings, f)

    @staticmethod
    def _now_iso():
        return datetime.now().isoformat(timespec="milliseconds")

    @staticmethod
    def _safe_name(text):
        if not text:
            return "unknown"
        return "".join(ch if ch.isalnum() or ch in "-_" else "_" for ch in text)

    def _ensure_game(self):
        if self.current_game is None:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            self._start_game(f"unknown_{ts}", ".internal.autoStart", "server", -1)

    def _start_game(self, game_uuid, method, direction, message_id):
        if self.current_game is not None:
            if self.current_game["game_uuid"] == game_uuid:
                return
            self._finalize_game("switch_game")

        self.current_game = {
            "game_uuid": game_uuid,
            "started_at": self._now_iso(),
            "start_method": method,
            "start_direction": direction,
            "start_message_id": message_id,
            "actions": [],
        }

    def _append_action(
        self, action_name, step, action_data, method, direction, message_id, source
    ):
        self._ensure_game()
        self.current_game["actions"].append(
            {
                "index": len(self.current_game["actions"]),
                "timestamp": self._now_iso(),
                "source": source,
                "method": method,
                "direction": direction,
                "message_id": message_id,
                "step": step,
                "name": action_name,
                "data": action_data,
            }
        )

    def _decode_sync_action(self, item):
        if item.get("data", "") == "":
            return {}
        try:
            raw = base64.b64decode(item["data"])
            proto_obj = getattr(pb, item["name"]).FromString(raw)
            return MessageToDict(
                proto_obj,
                preserving_proto_field_name=True,
                including_default_value_fields=True,
            )
        except Exception:
            return {"raw": item.get("data", "")}

    def _finalize_game(self, reason):
        if self.current_game is None:
            return

        payload = {
            "game_uuid": self.current_game["game_uuid"],
            "started_at": self.current_game["started_at"],
            "ended_at": self._now_iso(),
            "end_reason": reason,
            "start_method": self.current_game["start_method"],
            "start_direction": self.current_game["start_direction"],
            "start_message_id": self.current_game["start_message_id"],
            "action_count": len(self.current_game["actions"]),
            "actions": self.current_game["actions"],
        }

        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_uuid = self._safe_name(self.current_game["game_uuid"])
        output_path = os.path.join(self.output_dir, f"{safe_uuid}_{ts}.json")
        with open(output_path, "w", encoding="utf-8") as f:
            if self.pretty:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            else:
                json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

        logger.success(
            f"[round_recorder] 已写入：{output_path}（actions={len(self.current_game['actions'])}）"
        )
        self.current_game = None

    @staticmethod
    def _b64_to_bytes(text):
        if not text:
            return b""
        try:
            return base64.b64decode(text)
        except Exception:
            return b""

    def _parse_action_record(self, record_bytes):
        action_proto = pb.ActionPrototype()
        candidates = [record_bytes]
        try:
            candidates.append(liqi_decode(record_bytes))
        except Exception:
            pass

        parsed_action = None
        for candidate in candidates:
            try:
                action_proto.ParseFromString(candidate)
                if action_proto.name:
                    parsed_action = action_proto
                    break
            except Exception:
                continue

        if parsed_action is None:
            return {
                "parsed": False,
                "raw": base64.b64encode(record_bytes).decode("ascii"),
            }

        result = {
            "parsed": True,
            "step": parsed_action.step,
            "name": parsed_action.name,
        }
        action_name = parsed_action.name
        action_cls = getattr(pb, action_name, None)
        if action_cls is None:
            result["data"] = {
                "parsed": False,
                "raw": base64.b64encode(parsed_action.data).decode("ascii"),
            }
            return result

        action_data = None
        payload_candidates = [parsed_action.data]
        try:
            payload_candidates.append(liqi_decode(parsed_action.data))
        except Exception:
            pass

        for payload in payload_candidates:
            try:
                obj = action_cls.FromString(payload)
                action_data = MessageToDict(
                    obj,
                    preserving_proto_field_name=True,
                    including_default_value_fields=True,
                )
                break
            except Exception:
                continue

        if action_data is None:
            result["data"] = {
                "parsed": False,
                "raw": base64.b64encode(parsed_action.data).decode("ascii"),
            }
        else:
            result["data"] = {
                "parsed": True,
                "value": action_data,
            }
        return result

    def _parse_named_payload(self, name, payload_bytes):
        cls = getattr(pb, name.split(".")[-1], None)
        if cls is None:
            return {
                "parsed": False,
                "name": name,
                "raw": base64.b64encode(payload_bytes).decode("ascii"),
            }

        candidates = [payload_bytes]
        try:
            candidates.append(liqi_decode(payload_bytes))
        except Exception:
            pass

        for payload in candidates:
            try:
                obj = cls.FromString(payload)
                return {
                    "parsed": True,
                    "name": name,
                    "value": MessageToDict(
                        obj,
                        preserving_proto_field_name=True,
                        including_default_value_fields=True,
                    ),
                }
            except Exception:
                continue

        return {
            "parsed": False,
            "name": name,
            "raw": base64.b64encode(payload_bytes).decode("ascii"),
        }

    def _parse_game_record_blob(self, raw_bytes):
        wrapped_name = ""
        wrapped_data = raw_bytes
        wrapper = pb.Wrapper()
        try:
            wrapper.ParseFromString(raw_bytes)
            if wrapper.name and wrapper.data:
                wrapped_name = wrapper.name
                wrapped_data = wrapper.data
        except Exception:
            pass

        details = pb.GameDetailRecords()
        try:
            details.ParseFromString(wrapped_data)
        except Exception as exc:
            return {
                "parsed": False,
                "error": f"GameDetailRecords parse failed: {exc}",
                "raw_base64": base64.b64encode(raw_bytes).decode("ascii"),
            }

        parsed_records = []
        for item in details.records:
            parsed_records.append(self._parse_action_record(item))

        actions = []
        for item in details.actions:
            action_dict = MessageToDict(
                item,
                preserving_proto_field_name=True,
                including_default_value_fields=True,
            )
            if item.result:
                result_wrapper = pb.Wrapper()
                parsed_result = None
                try:
                    result_wrapper.ParseFromString(item.result)
                    if result_wrapper.name:
                        parsed_result = self._parse_named_payload(
                            result_wrapper.name, result_wrapper.data
                        )
                except Exception:
                    parsed_result = None

                if parsed_result is None:
                    action_dict["result_decoded"] = {
                        "parsed": False,
                        "raw": base64.b64encode(item.result).decode("ascii"),
                    }
                else:
                    action_dict["result_decoded"] = parsed_result

            actions.append(action_dict)

        return {
            "parsed": True,
            "wrapper_name": wrapped_name,
            "version": details.version,
            "records_count": len(details.records),
            "actions_count": len(details.actions),
            "records": parsed_records,
            "actions": actions,
            "bar": base64.b64encode(details.bar).decode("ascii") if details.bar else "",
        }

    def _write_paipu_record(self, data, direction, message_id):
        head = data.get("head", {})
        game_uuid = head.get("uuid", data.get("game_uuid", ""))
        safe_uuid = self._safe_name(game_uuid) if game_uuid else "unknown"
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = os.path.join(self.output_dir, f"paipu_{safe_uuid}_{ts}.json")

        raw_data_b64 = data.get("data", "")
        raw_data_bytes = self._b64_to_bytes(raw_data_b64)
        decoded_record = None
        if raw_data_bytes:
            decoded_record = self._parse_game_record_blob(raw_data_bytes)

        payload = {
            "type": "game_record",
            "captured_at": self._now_iso(),
            "method": self.PAIPU_METHOD,
            "direction": direction,
            "message_id": message_id,
            "game_uuid": game_uuid,
            "record": {
                "head": deepcopy(data.get("head", {})),
                "data_url": data.get("data_url", ""),
                "raw_data_base64": raw_data_b64,
                "raw_data_size": len(raw_data_bytes),
                "decoded": decoded_record,
            },
        }

        with open(output_path, "w", encoding="utf-8") as f:
            if self.pretty:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            else:
                json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))

        logger.success(f"[round_recorder] 已写入牌谱：{output_path}")

    def main(self, result, from_client):
        method = result.get("method", "")
        data = result.get("data", {})
        direction = "client" if from_client else "server"
        message_id = result.get("id", -1)

        if method == self.PAIPU_METHOD and not from_client:
            self._write_paipu_record(data, direction, message_id)

        if method in self.START_METHODS and "game_uuid" in data:
            self._start_game(data["game_uuid"], method, direction, message_id)

        if method == ".lq.FastTest.authGame" and from_client and "game_uuid" in data:
            self._start_game(data["game_uuid"], method, direction, message_id)

        if method == ".lq.ActionPrototype" and not from_client:
            self._append_action(
                action_name=data.get("name", ""),
                step=data.get("step"),
                action_data=deepcopy(data.get("data", {})),
                method=method,
                direction=direction,
                message_id=message_id,
                source="action_prototype",
            )

        if method == ".lq.FastTest.syncGame" and not from_client:
            actions = data.get("game_restore", {}).get("actions", [])
            for item in actions:
                self._append_action(
                    action_name=item.get("name", ""),
                    step=None,
                    action_data=self._decode_sync_action(item),
                    method=method,
                    direction=direction,
                    message_id=message_id,
                    source="sync_game_restore",
                )

        if method in self.END_METHODS and not from_client:
            self._finalize_game(method)

    def close(self):
        self._finalize_game("shutdown")
