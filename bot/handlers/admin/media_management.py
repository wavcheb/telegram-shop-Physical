from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.database.models import Permission
from bot.database.methods import check_item_cached
from bot.database.methods.media import (
    add_goods_media, get_goods_media, get_goods_media_count,
    delete_goods_media, MAX_MEDIA_PER_ITEM,
)
from bot.keyboards.inline import back, simple_buttons, media_upload_keyboard
from bot.logger_mesh import audit_logger
from bot.filters import HasPermissionFilter
from bot.i18n import localize
from bot.states import MediaManageFSM

router = Router()


@router.callback_query(F.data == 'manage_media', HasPermissionFilter(permission=Permission.SHOP_MANAGE))
async def manage_media_start(call: CallbackQuery, state: FSMContext):
    """Ask for product name to manage media."""
    await call.message.edit_text(
        localize('admin.goods.media.prompt.item_name'),
        reply_markup=back("goods_management"),
    )
    await state.set_state(MediaManageFSM.waiting_item_name)


@router.message(MediaManageFSM.waiting_item_name, F.text)
async def manage_media_select_item(message: Message, state: FSMContext):
    """Validate item name and show media management menu."""
    item_name = (message.text or "").strip()
    item = await check_item_cached(item_name)
    if not item:
        await message.answer(
            localize('admin.goods.position.not_found'),
            reply_markup=back('goods_management'),
        )
        await state.clear()
        return

    await state.update_data(media_item_name=item_name)
    await _show_media_menu(message, item_name)
    await state.set_state(MediaManageFSM.waiting_action)


async def _show_media_menu(target, item_name: str):
    """Show media management menu for an item. target can be Message or CallbackQuery.message."""
    media_count = get_goods_media_count(item_name)
    status = localize('admin.goods.media.status', count=media_count) if media_count else localize(
        'admin.goods.media.no_media')

    text = f"{localize('admin.goods.media.menu_title', name=item_name)}\n\n{status}"

    actions = [
        (localize("admin.goods.media.add_btn"), "media_action_add"),
    ]
    if media_count > 0:
        actions.append((localize("admin.goods.media.delete_btn"), "media_action_delete"))
    actions.append((localize("btn.back"), "goods_management"))

    markup = simple_buttons(actions, per_row=1)

    if hasattr(target, 'edit_text'):
        try:
            await target.edit_text(text, reply_markup=markup)
        except Exception:
            await target.answer(text, reply_markup=markup)
    else:
        await target.answer(text, reply_markup=markup)


@router.callback_query(F.data == 'media_action_add', MediaManageFSM.waiting_action)
async def media_action_add(call: CallbackQuery, state: FSMContext):
    """Start adding media to an existing product."""
    data = await state.get_data()
    item_name = data.get('media_item_name')
    current_count = get_goods_media_count(item_name)

    if current_count >= MAX_MEDIA_PER_ITEM:
        await call.message.edit_text(
            localize('admin.goods.media.limit_reached', max=MAX_MEDIA_PER_ITEM),
            reply_markup=back('goods_management'),
        )
        await state.clear()
        return

    await call.message.edit_text(
        localize('admin.goods.media.upload_prompt'),
        reply_markup=media_upload_keyboard(done_cb="manage_media_done"),
    )
    await state.set_state(MediaManageFSM.waiting_media_upload)


@router.callback_query(F.data == 'manage_media_done', MediaManageFSM.waiting_media_upload)
async def manage_media_done(call: CallbackQuery, state: FSMContext):
    """Finish adding media to existing product."""
    data = await state.get_data()
    item_name = data.get('media_item_name')
    media_count = get_goods_media_count(item_name)

    await call.message.edit_text(
        localize('admin.goods.media.done', name=item_name)
        + "\n" + localize('admin.goods.media.status', count=media_count),
        reply_markup=back('goods_management'),
    )
    await state.clear()


@router.message(MediaManageFSM.waiting_media_upload, F.photo)
async def handle_photo_upload_manage(message: Message, state: FSMContext):
    """Handle photo upload for existing product."""
    data = await state.get_data()
    item_name = data.get('media_item_name')

    current_count = get_goods_media_count(item_name)
    if current_count >= MAX_MEDIA_PER_ITEM:
        await message.answer(
            localize('admin.goods.media.limit_reached', max=MAX_MEDIA_PER_ITEM),
            reply_markup=media_upload_keyboard(done_cb="manage_media_done"),
        )
        return

    file_id = message.photo[-1].file_id
    add_goods_media(item_name, file_id, 'photo')
    current_count += 1

    await message.answer(
        localize('admin.goods.media.added_photo', count=current_count, max=MAX_MEDIA_PER_ITEM),
        reply_markup=media_upload_keyboard(done_cb="manage_media_done"),
    )


@router.message(MediaManageFSM.waiting_media_upload, F.video)
async def handle_video_upload_manage(message: Message, state: FSMContext):
    """Handle video upload for existing product."""
    data = await state.get_data()
    item_name = data.get('media_item_name')

    current_count = get_goods_media_count(item_name)
    if current_count >= MAX_MEDIA_PER_ITEM:
        await message.answer(
            localize('admin.goods.media.limit_reached', max=MAX_MEDIA_PER_ITEM),
            reply_markup=media_upload_keyboard(done_cb="manage_media_done"),
        )
        return

    file_id = message.video.file_id
    add_goods_media(item_name, file_id, 'video')
    current_count += 1

    await message.answer(
        localize('admin.goods.media.added_video', count=current_count, max=MAX_MEDIA_PER_ITEM),
        reply_markup=media_upload_keyboard(done_cb="manage_media_done"),
    )


@router.message(MediaManageFSM.waiting_media_upload)
async def handle_invalid_media_upload_manage(message: Message, state: FSMContext):
    """Handle non-photo/video messages during media upload."""
    await message.answer(
        localize('admin.goods.media.invalid_type'),
        reply_markup=media_upload_keyboard(done_cb="manage_media_done"),
    )


@router.callback_query(F.data == 'media_action_delete', MediaManageFSM.waiting_action)
async def media_action_delete(call: CallbackQuery, state: FSMContext):
    """Show list of media to delete."""
    data = await state.get_data()
    item_name = data.get('media_item_name')
    media_list = get_goods_media(item_name)

    if not media_list:
        await call.message.edit_text(
            localize('admin.goods.media.no_media'),
            reply_markup=back('goods_management'),
        )
        await state.clear()
        return

    buttons = []
    for m in media_list:
        type_icon = "📷" if m['media_type'] == 'photo' else "🎥"
        buttons.append((f"{type_icon} #{m['position']}", f"del_media_{m['id']}"))
    buttons.append((localize("btn.back"), "media_back_to_menu"))

    await call.message.edit_text(
        localize('admin.goods.media.select_to_delete'),
        reply_markup=simple_buttons(buttons, per_row=3),
    )
    await state.set_state(MediaManageFSM.waiting_media_delete)


@router.callback_query(F.data.startswith('del_media_'), MediaManageFSM.waiting_media_delete)
async def delete_media_item(call: CallbackQuery, state: FSMContext):
    """Delete a specific media file."""
    media_id = int(call.data.replace('del_media_', ''))
    delete_goods_media(media_id)

    data = await state.get_data()
    item_name = data.get('media_item_name')

    audit_logger.info(f'Admin {call.from_user.id} deleted media #{media_id} from "{item_name}"')

    # Show updated delete list or return to menu
    media_list = get_goods_media(item_name)
    if not media_list:
        await call.message.edit_text(
            localize('admin.goods.media.deleted') + "\n" + localize('admin.goods.media.no_media'),
            reply_markup=back('goods_management'),
        )
        await state.clear()
        return

    buttons = []
    for m in media_list:
        type_icon = "📷" if m['media_type'] == 'photo' else "🎥"
        buttons.append((f"{type_icon} #{m['position']}", f"del_media_{m['id']}"))
    buttons.append((localize("btn.back"), "media_back_to_menu"))

    await call.message.edit_text(
        localize('admin.goods.media.deleted') + "\n\n" + localize('admin.goods.media.select_to_delete'),
        reply_markup=simple_buttons(buttons, per_row=3),
    )


@router.callback_query(F.data == 'media_back_to_menu')
async def media_back_to_menu(call: CallbackQuery, state: FSMContext):
    """Go back to media management menu."""
    data = await state.get_data()
    item_name = data.get('media_item_name')
    if item_name:
        await _show_media_menu(call.message, item_name)
        await state.set_state(MediaManageFSM.waiting_action)
    else:
        await call.message.edit_text(
            localize('admin.goods.menu.title'),
            reply_markup=back('goods_management'),
        )
        await state.clear()
