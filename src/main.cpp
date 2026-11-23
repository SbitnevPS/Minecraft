#include <Geode/Geode.hpp>
#include <Geode/modify/GameManager.hpp>
#include <Geode/modify/GJGarageLayer.hpp>
#include <Geode/ui/Popup.hpp>
#include <Geode/ui/General.hpp>

using namespace geode::prelude;

namespace {
bool unlockEnabled() {
    return Mod::get()->getSavedValue<bool>("unlock-enabled", true);
}
}

class UnlockToolsPopup : public Popup<> {
protected:
    CCLabelBMFont* m_status = nullptr;
    bool setup() override {
        this->setTitle("Icon Pack Tools");
        const auto size = m_mainLayer->getContentSize();
        auto caption = CCLabelBMFont::create("All icons and colors", "goldFont.fnt");
        caption->setScale(.62f);
        caption->setPosition({size.width / 2.f, size.height / 2.f + 40.f});
        m_mainLayer->addChild(caption);

        m_status = CCLabelBMFont::create(unlockEnabled() ? "ON" : "OFF", "bigFont.fnt");
        m_status->setScale(.5f);
        m_status->setPosition({size.width / 2.f, size.height / 2.f + 14.f});
        m_mainLayer->addChild(m_status);

        auto menu = CCMenu::create();
        menu->setPosition({size.width / 2.f, size.height / 2.f - 28.f});
        m_mainLayer->addChild(menu);
        auto toggleButton = CCMenuItemSpriteExtra::create(
            ButtonSprite::create("ON / OFF"), this, menu_selector(UnlockToolsPopup::onToggle)
        );
        toggleButton->setScale(.7f);
        toggleButton->setPosition({-72.f, 0.f});
        menu->addChild(toggleButton);

        auto removeButton = CCMenuItemSpriteExtra::create(
            ButtonSprite::create("Remove"), this, menu_selector(UnlockToolsPopup::onRemove)
        );
        removeButton->setScale(.7f);
        removeButton->setPosition({72.f, 0.f});
        menu->addChild(removeButton);

        auto hint = CCLabelBMFont::create("Remove: restart game to finish", "chatFont.fnt");
        hint->setScale(.62f);
        hint->setPosition({size.width / 2.f, 25.f});
        m_mainLayer->addChild(hint);
        return true;
    }

    void onToggle(CCObject*) {
        const bool on = !unlockEnabled();
        Mod::get()->setSavedValue<bool>("unlock-enabled", on);
        if (m_status) m_status->setString(on ? "ON" : "OFF");
    }

    void onRemove(CCObject*) {
        geode::createQuickPopup(
            "Remove Icon Pack?",
            "Delete this mod and its settings? Restart the game afterwards.",
            "Cancel", "Delete",
            [](FLAlertLayer*, bool confirmed) {
                if (!confirmed) return;
                Mod::get()->setSavedValue<bool>("unlock-enabled", false);
                auto result = Mod::get()->uninstall(true);
                if (result) {
                    FLAlertLayer::create("Removal requested",
                        "Restart Geometry Dash to finish uninstalling the pack.", "OK")->show();
                } else {
                    FLAlertLayer::create("Could not remove",
                        "Open Geode > Installed > Icon & Color Unlock Pack > Uninstall.",
                        "OK")->show();
                }
            }
        );
    }

public:
    static UnlockToolsPopup* create() {
        auto* popup = new UnlockToolsPopup();
        if (popup && popup->initAnchored(310.f, 184.f)) {
            popup->autorelease();
            return popup;
        }
        CC_SAFE_DELETE(popup);
        return nullptr;
    }
};

class $modify(UnlockPackGameManager, GameManager) {
    bool isIconUnlocked(int iconID, IconType type) {
        if (unlockEnabled()) return true;
        return GameManager::isIconUnlocked(iconID, type);
    }
    bool isColorUnlocked(int colorID, UnlockType type) {
        if (unlockEnabled()) return true;
        return GameManager::isColorUnlocked(colorID, type);
    }
};

class $modify(UnlockPackGarage, GJGarageLayer) {
    bool init() {
        if (!GJGarageLayer::init()) return false;
        const auto size = CCDirector::sharedDirector()->getWinSize();
        auto menu = CCMenu::create();
        menu->setID("icon-unlock-pack-tools-menu");
        menu->setPosition({size.width - 31.f, size.height / 2.f + 57.f});
        this->addChild(menu, 25);
        auto button = CCMenuItemSpriteExtra::create(
            ButtonSprite::create("Tools"), this, menu_selector(UnlockPackGarage::onUnlockPackTools)
        );
        button->setScale(.54f);
        button->setID("icon-unlock-pack-tools-button");
        menu->addChild(button);
        return true;
    }

    void onUnlockPackTools(CCObject*) {
        if (auto popup = UnlockToolsPopup::create()) popup->show();
    }
};
